from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, func

from app.core.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(127), nullable=False)
    extension = Column(String(32), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="UPLOADED", index=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_uploads_project_created", "project_id", "created_at"),
    )
