import time
from app.core.celery_app import celery_app
from analysis_engine.cloner import RepositoryCloner
from analysis_engine.parser import CodebaseParser
from app.core.database import SessionLocal
from app.models.analysis import AnalysisRun

@celery_app.task(bind=True)
def run_full_analysis(self, repo_url: str, repo_id: int, analysis_id: int):
    """
    Orchestrates the full analysis pipeline for a repository.
    """
    db = SessionLocal()
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    
    if not analysis:
        return "Analysis not found"

    try:
        analysis.status = "Active"
        db.commit()
        
        start_time = time.time()
        
        # 1. Clone
        cloner = RepositoryCloner()
        local_path = cloner.clone(repo_url, str(repo_id))
        
        # 2. Parse & Analyze
        parser = CodebaseParser(local_path)
        parser.scan_files()
        structure = parser.parse_structure()
        
        # 3. Graph Analysis
        from analysis_engine.graph_analyzer import GraphAnalyzer
        analyzer = GraphAnalyzer(parser.graph)
        file_metrics = {f["path"]: f["metrics"] for f in structure["files"]}
        risk_scores = analyzer.get_risk_scores(file_metrics)
        d3_data = analyzer.get_d3_data(file_metrics)
        
        # 4. Process Results (Placeholder for storage logic)
        # In a real scenario, we would iterate through structure['files'] 
        # and update File and RiskScore models.
        
        # Cleanup
        cloner.cleanup(local_path)
        
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
