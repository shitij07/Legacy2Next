from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisFile(Base):
    __tablename__ = "analysis_files"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    relative_path = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    extension = Column(String(32), nullable=True)
    file_size = Column(Integer, nullable=False)
    lines_of_code = Column(Integer, nullable=True)
    language = Column(String(64), nullable=True)
    is_directory = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    analysis = relationship("Analysis", backref="analysis_files")

    __table_args__ = (
        Index("ix_analysis_files_analysis_path", "analysis_id", "relative_path", unique=True),
        Index("ix_analysis_files_extension", "analysis_id", "extension"),
    )
