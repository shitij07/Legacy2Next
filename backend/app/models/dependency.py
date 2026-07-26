import json

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(128), nullable=True)
    type = Column(String(32), nullable=False)
    source_file = Column(String(1024), nullable=True)
    source_files = Column(Text, nullable=True)
    ecosystem = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    analysis = relationship("Analysis", backref="dependencies")

    __table_args__ = (
        Index("ix_dependencies_ecosystem", "analysis_id", "ecosystem"),
    )

    @property
    def source_files_list(self) -> list[str]:
        if self.source_files is None:
            return []
        return json.loads(self.source_files)
