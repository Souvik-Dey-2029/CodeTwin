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

class ImpactSimulationRequest(BaseModel):
    file_path: str

class RefactorProposalOut(BaseModel):
    file_path: str
    complexity: int
    centrality: float
    reason: str
    suggested_action: str

class AffectedNode(BaseModel):
    id: str
    distance: int
    centrality: float

class ImpactSimulationOut(BaseModel):
    target: str
    impact_score: float
    affected_nodes: List[AffectedNode]

class DashboardSummaryOut(BaseModel):
    health_score: float
    status: str
    analysis_id: Optional[int]
    god_object_count: int
    total_files: int
    total_dependencies: int
    risk_level: str
