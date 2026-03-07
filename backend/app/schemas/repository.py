from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Any
from datetime import datetime

class RepositoryBase(BaseModel):
    name: str
    github_url: str
    default_branch: Optional[str] = "main"

class RepositoryCreate(BaseModel):
    github_url: str

class RepositoryOut(RepositoryBase):
    id: int
    health_score: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AnalysisOut(BaseModel):
    id: int
    repo_id: int
    sha: Optional[str]
    status: str
    runtime_ms: Optional[int]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
