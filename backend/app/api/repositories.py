from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import os
from pathlib import Path
from sqlalchemy.orm import Session
from typing import List
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
