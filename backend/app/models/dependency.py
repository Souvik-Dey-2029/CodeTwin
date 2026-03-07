from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True, index=True)
    source_file_id = Column(Integer, ForeignKey("files.id"))
    target_file_id = Column(Integer, ForeignKey("files.id"))
    dependency_type = Column(String)  # e.g., "Internal", "External"
