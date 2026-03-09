from app.core.database import SessionLocal
from app.models.analysis import AnalysisRun
from app.models.repository import Repository
import json

db = SessionLocal()
try:
    analysis = db.query(AnalysisRun).filter(AnalysisRun.status == "Done").first()
    if not analysis:
        print("No completed analysis found.")
    else:
        print(f"Analysis ID: {analysis.id}")
        print(f"Graph Data Type: {type(analysis.graph_data)}")
        print(f"Refactor Data Type: {type(analysis.refactor_data)}")
        print(f"Refactor Data Content: {analysis.refactor_data}")
        
        repo = db.query(Repository).filter(Repository.id == analysis.repo_id).first()
        print(f"Repo Health: {repo.health_score}")
finally:
    db.close()
