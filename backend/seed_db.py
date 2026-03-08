import sys
import os
from sqlalchemy.orm import Session

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
from app.models.repository import Repository
from app.models.analysis import AnalysisRun
import app.models

# Create tables
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    try:
        # Check if repo 1 exists
        repo = db.query(Repository).filter(Repository.id == 1).first()
        if not repo:
            repo = Repository(
                id=1,
                name="CodeTwin-Demo",
                github_url="https://github.com/Souvik-Dey-2029/CodeTwin",
                default_branch="main",
                health_score=85.5
            )
            db.add(repo)
            db.commit()
            print("Seeded repository 1")
        
        # Check if analysis exists
        analysis = db.query(AnalysisRun).filter(AnalysisRun.repo_id == 1).first()
        if not analysis:
            analysis = AnalysisRun(
                repo_id=1,
                status="Done",
                runtime_ms=1200
            )
            db.add(analysis)
            db.commit()
            print("Seeded analysis for repo 1")
            
    finally:
        db.close()

if __name__ == "__main__":
    seed()
