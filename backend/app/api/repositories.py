from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import os
from pathlib import Path
from sqlalchemy.orm import Session
import httpx
import base64
from typing import List
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

from app.core.database import get_db
from app.models.repository import Repository
from app.models.analysis import AnalysisRun
from app.schemas.repository import (
    RepositoryCreate, 
    RepositoryOut, 
    AnalysisOut, 
    RefactorProposalOut, 
    ImpactSimulationRequest, 
    ImpactSimulationOut,
    DashboardSummaryOut
)
from app.services.tasks import run_full_analysis
import networkx as nx
from analysis_engine.graph_analyzer import GraphAnalyzer

router = APIRouter()

@router.get("/", response_model=List[RepositoryOut])
def list_repositories(db: Session = Depends(get_db)):
    return db.query(Repository).order_by(Repository.id.desc()).limit(10).all()

@router.post("/", response_model=RepositoryOut)
def create_repository(repo_in: RepositoryCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if exists
    db_repo = db.query(Repository).filter(Repository.github_url == repo_in.github_url).first()
    if not db_repo:
        # Extract name from URL (simple logic)
        name = repo_in.github_url.split("/")[-1].replace(".git", "")
        db_repo = Repository(name=name, github_url=repo_in.github_url)
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)

    # Create an analysis run entry
    analysis = AnalysisRun(repo_id=db_repo.id, status="Queue")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Trigger Analysis via BackgroundTasks (More robust for local dev)
    from app.services.tasks import run_analysis_logic
    background_tasks.add_task(run_analysis_logic, db_repo.github_url, db_repo.id, analysis.id)

    return db_repo

@router.get("/{repo_id}/status", response_model=AnalysisOut)
def get_analysis_status(repo_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id).order_by(AnalysisRun.id.desc()).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for this repository")
    return analysis

@router.post("/{repo_id}/reanalyze", response_model=AnalysisOut)
def reanalyze_repository(repo_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not db_repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    analysis = AnalysisRun(repo_id=db_repo.id, status="Queue")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    from app.services.tasks import run_analysis_logic
    background_tasks.add_task(run_analysis_logic, db_repo.github_url, db_repo.id, analysis.id)
    return analysis

@router.get("/{repo_id}", response_model=RepositoryOut)
def get_repository(repo_id: int, db: Session = Depends(get_db)):
    db_repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not db_repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return db_repo

@router.get("/{repo_id}/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    
    if not analysis:
        # Check for in-progress analysis to give better status
        latest = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id).order_by(AnalysisRun.id.desc()).first()
        status = latest.status if latest else "Queue"
        return {
            "health_score": repo.health_score,
            "status": status,
            "analysis_id": latest.id if latest else None,
            "god_object_count": 0,
            "total_files": 0,
            "total_dependencies": 0,
            "risk_level": "Unknown"
        }
    
    god_objects = analysis.refactor_data or []
    graph = analysis.graph_data or {"nodes": [], "links": []}
    
    # Calculate risk level
    risk_level = "Low"
    if repo.health_score < 60 or len(god_objects) > 5:
        risk_level = "High"
    elif repo.health_score < 85 or len(god_objects) > 2:
        risk_level = "Medium"
        
    return {
        "health_score": repo.health_score,
        "status": analysis.status,
        "analysis_id": analysis.id,
        "god_object_count": len(god_objects),
        "total_files": len(graph.get("nodes", [])),
        "total_dependencies": len(graph.get("links", [])),
        "risk_level": risk_level
    }

@router.get("/{repo_id}/graph")
def get_repository_graph(repo_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.graph_data:
        # Fallback to empty graph if no analysis done
        return {"nodes": [], "links": []}
    return analysis.graph_data

@router.get("/{repo_id}/heatmap")
def get_repository_heatmap(repo_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.heatmap_data:
        return {"name": "root", "children": []}
    return analysis.heatmap_data

@router.get("/{repo_id}/refactor-proposals", response_model=List[RefactorProposalOut])
def get_refactor_proposals(repo_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.refactor_data:
        return []
    
    # Process refactor data into the schema format
    proposals = []
    for item in analysis.refactor_data:
        proposals.append({
            "file_path": item["file_path"],
            "complexity": item["complexity"],
            "centrality": item["centrality"],
            "reason": item["reason"],
            "suggested_action": f"Extract logic from {item['file_path']} to reduce architectural pressure."
        })
    return proposals

@router.post("/{repo_id}/simulate-impact", response_model=ImpactSimulationOut)
def simulate_impact(repo_id: int, req: ImpactSimulationRequest, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.graph_data:
        raise HTTPException(status_code=404, detail="No completed analysis found for this repository")

    # Reconstruct graph from JSON
    graph = nx.DiGraph()
    for node in analysis.graph_data["nodes"]:
        graph.add_node(node["id"], **node)
    for link in analysis.graph_data["links"]:
        graph.add_edge(link["source"], link["target"])

    analyzer = GraphAnalyzer(graph)
    result = analyzer.simulate_blast_radius(req.file_path)
    return result

@router.get("/{repo_id}/file-content")
def get_file_content(repo_id: int, path: str):
    # Construct base path (matches cloner.py default)
    base_dir = Path("C:/tmp/codetwin") if os.name == "nt" else Path("/tmp/codetwin")
    file_path = base_dir / str(repo_id) / path
    
    # Security check: ensure path is within the repo directory
    try:
        resolved_file = file_path.resolve()
        resolved_repo = (base_dir / str(repo_id)).resolve()
        if not str(resolved_file).startswith(str(resolved_repo)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repo_id}/ai-advice")
async def get_ai_refactor_advice(repo_id: int, file_path_b64: str, db: Session = Depends(get_db)):
    try:
        file_path = base64.urlsafe_b64decode(file_path_b64.encode("utf-8")).decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Base64 file_path")

    # Fetch complexity data
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.refactor_data:
        raise HTTPException(status_code=404, detail="Analysis data not found")

    metrics = next((item for item in analysis.refactor_data if item["file_path"] == file_path), None)
    complexity = metrics["complexity"] if metrics else "Unknown"

    # Fetch raw code
    base_dir = Path("C:/tmp/codetwin") if os.name == "nt" else Path("/tmp/codetwin")
    real_path = base_dir / str(repo_id) / file_path
    
    try:
        resolved_file = real_path.resolve()
        resolved_repo = (base_dir / str(repo_id)).resolve()
        if not str(resolved_file).startswith(str(resolved_repo)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    if not real_path.exists():
        raise HTTPException(status_code=404, detail="Local code not found")

    try:
        with open(real_path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Error reading file")

    if not OPENROUTER_API_KEY:
        return {"advice": "> [!NOTE]\n> Skipping AI Request: OPENROUTER_API_KEY not configured in backend/.env"}

    prompt = f"You are a Senior Software Architect assisting in a Codebase Digital Twin project. The file '{file_path}' has been structurally flagged as a heavy 'God Object' with a complexity score of {complexity}. Provide a targeted, strategic plan for modular refactoring. Keep it actionable. Here is the code:\n\n```\n{code_content}\n```\n\nReturn EXACTLY a well-formatted minimalist markdown payload detailing step-by-step refactoring, followed by a brief example refactored code snippet if practical."

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CodeTwin Predictive Engine"
                },
                json={
                    "model": "google/gemini-1.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )
            response.raise_for_status()
            ai_data = response.json()
            advice = ai_data["choices"][0]["message"]["content"]
            return {"advice": advice}
    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return {"advice": f"**API Error:** Failed to fetch AI suggestion from OpenRouter Gemini Flash. `[Exception: {str(e)}]`"}

@router.get("/{repo_id}/dead-code")
def get_dead_code_analysis(repo_id: int, db: Session = Depends(get_db)):
    """Get dead code detection results."""
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.dead_code_data:
        return {"dead_functions": [], "unused_imports": [], "total_files_analyzed": 0}
    return analysis.dead_code_data

@router.get("/{repo_id}/dependencies")
def get_dependency_analysis(repo_id: int, db: Session = Depends(get_db)):
    """Get unused and missing dependency analysis results."""
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.dependency_data:
        return {"unused_dependencies": [], "missing_dependencies": [], "total_declared": 0, "issue_count": 0}
    return analysis.dependency_data

@router.get("/{repo_id}/dead-code/{func_index}/explanation")
async def explain_dead_function(repo_id: int, func_index: int, db: Session = Depends(get_db)):
    """Generate AI explanation for a dead function."""
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.dead_code_data:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    dead_funcs = analysis.dead_code_data.get("dead_functions", [])
    if func_index >= len(dead_funcs):
        raise HTTPException(status_code=400, detail="Invalid function index")
    
    func = dead_funcs[func_index]
    
    if not OPENROUTER_API_KEY:
        return {"explanation": "OPENROUTER_API_KEY not configured. This function appears to be completely unused in the codebase."}
    
    prompt = f"""You are a Code Quality Analyzer. A JavaScript/TypeScript function has been flagged as dead code:

**Function Name**: {func['name']}
**File**: {func['file']}
**Type**: {func['type']}
**Confidence**: {func.get('confidence', 0.8) * 100:.0f}%

This function is never called anywhere in the codebase. Provide:
1. Why it's likely safe to remove
2. Potential reasons it might be kept (edge cases)
3. A removal strategy if it's decided to be deleted

Keep the response concise and actionable."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CodeTwin Dead Code Analyzer"
                },
                json={
                    "model": "google/gemini-1.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            ai_data = response.json()
            explanation = ai_data["choices"][0]["message"]["content"]
            return {"explanation": explanation, "confidence": func.get("confidence", 0.8)}
    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return {"explanation": f"This function '{func['name']}' is never called anywhere in the codebase, making it safe to remove unless it's part of a public API.", "confidence": func.get("confidence", 0.8)}

@router.get("/{repo_id}/dependencies/{dep_index}/explanation")
async def explain_unused_dependency(repo_id: int, dep_index: int, db: Session = Depends(get_db)):
    """Generate AI explanation for an unused dependency."""
    analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "Done").order_by(AnalysisRun.id.desc()).first()
    if not analysis or not analysis.dependency_data:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    unused_deps = analysis.dependency_data.get("unused_dependencies", [])
    if dep_index >= len(unused_deps):
        raise HTTPException(status_code=400, detail="Invalid dependency index")
    
    dep = unused_deps[dep_index]
    
    if not OPENROUTER_API_KEY:
        return {"explanation": f"The dependency '{dep['name']}' is declared but never imported."}
    
    prompt = f"""You are a JavaScript/Node.js package analyzer. A dependency is declared in package.json but never used:

**Package Name**: {dep['name']}
**Version**: {dep['version']}
**Type**: {dep['type']}
**Confidence**: {dep.get('confidence', 0.7) * 100:.0f}%

Provide:
1. Why it's likely safe to remove
2. Common reasons developers might keep it (security patches, peer dependencies, etc)
3. Removal command to uninstall it

Be concise and practical."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CodeTwin Dependency Analyzer"
                },
                json={
                    "model": "google/gemini-1.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            ai_data = response.json()
            explanation = ai_data["choices"][0]["message"]["content"]
            return {"explanation": explanation, "confidence": dep.get("confidence", 0.7)}
    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return {"explanation": f"The package '{dep['name']}' is declared in package.json but doesn't appear to be imported anywhere. It's likely safe to remove via 'npm uninstall {dep['name']}'.", "confidence": dep.get("confidence", 0.7)}
