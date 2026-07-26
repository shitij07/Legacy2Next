from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisTechnology(Base):
    __tablename__ = "analysis_technologies"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    technology_id = Column(Integer, ForeignKey("technologies.id"), nullable=False)
    evidence = Column(String(1024), nullable=True)
    confidence = Column(String(16), nullable=False, default="high")

    analysis = relationship("Analysis", backref="analysis_technologies")
    technology = relationship("Technology", backref="analysis_technologies")
