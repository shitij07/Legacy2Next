from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    analysis_a_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    analysis_b_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    summary = Column(Text, nullable=True)
    comparison_data = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="comparisons")
    analysis_a = relationship("Analysis", foreign_keys=[analysis_a_id], backref="comparisons_as_a")
    analysis_b = relationship("Analysis", foreign_keys=[analysis_b_id], backref="comparisons_as_b")
