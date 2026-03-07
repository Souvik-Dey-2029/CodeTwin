from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    sha = Column(String)
    status = Column(String)  # Queue, Active, Done, Error
    runtime_ms = Column(Integer, nullable=True)
    error_log = Column(Text, nullable=True)

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    category = Column(String)  # Logic, Coupling, Churn
    score = Column(Float)
    rationale = Column(Text)

class RefactorProposal(Base):
    __tablename__ = "refactor_proposals"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    issue_type = Column(String)
    suggested_diff = Column(Text)
    estimated_effort = Column(String)  # Easy, Medium, Hard
