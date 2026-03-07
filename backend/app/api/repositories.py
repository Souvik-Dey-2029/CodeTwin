from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.repository import Repository
from app.models.analysis import AnalysisRun
from app.schemas.repository import RepositoryCreate, RepositoryOut, AnalysisOut
from app.services.tasks import run_full_analysis

router = APIRouter()

@router.post("/", response_model=RepositoryOut)
def create_repository(repo_in: RepositoryCreate, db: Session = Depends(get_db)):
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

    # Trigger Celery Task
    run_full_analysis.delay(db_repo.github_url, db_repo.id, analysis.id)

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
