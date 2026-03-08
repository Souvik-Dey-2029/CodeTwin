import time
from app.core.celery_app import celery_app
# Lazy imports inside task to avoid breaking API on startup due to missing dependencies
from app.core.database import SessionLocal
from app.models.analysis import AnalysisRun

@celery_app.task(bind=True)
def run_full_analysis(self, repo_url: str, repo_id: int, analysis_id: int):
    """
    Celery task wrapper.
    """
    return run_analysis_logic(repo_url, repo_id, analysis_id)

def run_analysis_logic(repo_url: str, repo_id: int, analysis_id: int):
    """
    Core analysis logic that can be run by Celery or FastAPI BackgroundTasks.
    """
    db = SessionLocal()
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    
    if not analysis:
        return "Analysis not found"

    try:
        analysis.status = "Active"
        db.commit()
        
        start_time = time.time()
        
        # 1. Clone (Lazy Import)
        from analysis_engine.cloner import RepositoryCloner
        cloner = RepositoryCloner()
        local_path = cloner.clone(repo_url, str(repo_id))
        
        # 2. Parse & Analyze (Lazy Import)
        from analysis_engine.parser import CodebaseParser
        parser = CodebaseParser(local_path)
        parser.scan_files()
        structure = parser.parse_structure()
        
        # 3. Graph Analysis
        from analysis_engine.graph_analyzer import GraphAnalyzer
        analyzer = GraphAnalyzer(parser.graph)
        file_metrics = {f["path"]: f["metrics"] for f in structure["files"]}
        
        # Save results to the analysis model
        analysis.graph_data = analyzer.get_d3_data(file_metrics)
        analysis.heatmap_data = analyzer.get_heatmap_data(file_metrics)
        analysis.refactor_data = analyzer.detect_god_objects(file_metrics)
        
        # Calculate and update Repository Health Score
        risk_scores = analyzer.get_risk_scores(file_metrics)
        if risk_scores:
            avg_risk = sum(risk_scores.values()) / len(risk_scores)
            health = max(0, min(100, 100 - (avg_risk * 10))) # Scale risk to 0-100 health
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            if repo:
                repo.health_score = round(health, 2)
        
        # Cleanup (Commented out to allow live 'Digital Twin' exploration)
        # cloner.cleanup(local_path)
        
        # Finalize
        analysis.status = "Done"
        analysis.runtime_ms = int((time.time() - start_time) * 1000)
        db.commit()
        
        return {"status": "success", "runtime": analysis.runtime_ms}
        
    except Exception as e:
        analysis.status = "Error"
        analysis.error_log = str(e)
        db.commit()
        print(f"Analysis failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
