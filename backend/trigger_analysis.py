from app.core.database import SessionLocal
from app.models.analysis import AnalysisRun
from app.models.repository import Repository
from app.services.tasks import run_analysis_logic
import os

db = SessionLocal()
try:
    analysis = db.query(AnalysisRun).filter(AnalysisRun.status == "Queue").first()
    if not analysis:
        print("No analysis in queue.")
    else:
        repo = db.query(Repository).filter(Repository.id == analysis.repo_id).first()
        print(f"Triggering analysis for {repo.name} (ID: {repo.id})...")
        result = run_analysis_logic(repo.github_url, repo.id, analysis.id)
        print(f"Analysis triggered. Result: {result}")
finally:
    db.close()
