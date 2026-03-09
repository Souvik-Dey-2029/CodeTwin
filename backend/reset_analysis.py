from app.core.database import SessionLocal
from app.models.analysis import AnalysisRun
from app.models.repository import Repository

db = SessionLocal()
try:
    print("Clearing analysis_runs...")
    db.query(AnalysisRun).delete()
    db.commit()
    print("Cleared.")
    
    repos = db.query(Repository).all()
    for repo in repos:
        print(f"Re-queueing analysis for {repo.name}")
        analysis = AnalysisRun(repo_id=repo.id, status="Queue")
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # In a real environment we'd trigger the background task here.
        # For this script we just want to ensure the next request triggers it if polling is active
        # Or I can manually run the logic here in a small loop if I import run_analysis_logic.
finally:
    db.close()
