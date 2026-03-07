from app.models.repository import Repository
from app.models.file import File
from app.models.dependency import Dependency
from app.models.analysis import AnalysisRun, RiskScore, RefactorProposal

# This ensures all models are registered with the Base
__all__ = [
    "Repository",
    "File",
    "Dependency",
    "AnalysisRun",
    "RiskScore",
    "RefactorProposal",
]
