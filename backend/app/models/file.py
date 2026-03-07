from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    path = Column(String, index=True)
    extension = Column(String)
    loc = Column(Integer)
    complexity_score = Column(Float, default=0.0)
    maintainability_index = Column(Float, default=0.0)

    repository = relationship("Repository", backref="files")
