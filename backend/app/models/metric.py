from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    key = Column(String(64), nullable=False)
    value = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    analysis = relationship("Analysis", backref="metrics")

    __table_args__ = (
        Index("ix_metrics_key", "analysis_id", "key", unique=True),
    )
