from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisWarning(Base):
    __tablename__ = "analysis_warnings"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    detector_name = Column(String(64), nullable=False)
    message = Column(String(1024), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    analysis = relationship("Analysis", backref="analysis_warnings")
