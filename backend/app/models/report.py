import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReportFormat(str, enum.Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class ReportStatus(str, enum.Enum):
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    format = Column(Enum(ReportFormat), nullable=False, default=ReportFormat.MARKDOWN)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.GENERATING)
    content = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", backref="reports")
    analysis = relationship("Analysis", backref="reports")
    user = relationship("User", backref="reports")
