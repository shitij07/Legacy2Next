from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())
