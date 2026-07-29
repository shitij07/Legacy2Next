from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

T = TypeVar("T")


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class ReportStatus(str, Enum):
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class ReportCreate(BaseModel):
    project_id: int = Field(..., ge=1)
    analysis_id: int = Field(..., ge=1)
    format: ReportFormat = ReportFormat.MARKDOWN
    title: str = Field(default="Analysis Report", min_length=1, max_length=255)


class ReportResponse(BaseModel):
    id: int
    project_id: int
    analysis_id: int
    user_id: int
    title: str
    format: ReportFormat
    status: ReportStatus
    content: str | None = None
    file_path: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ReportSummary(BaseModel):
    id: int
    project_id: int
    analysis_id: int
    title: str
    format: ReportFormat
    status: ReportStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    items: list[ReportSummary]
    total: int
    page: int
    size: int
    pages: int
