from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.config import ConfigDict

T = TypeVar("T")


class AnalysisResponse(BaseModel):
    analysis_id: int
    status: str
    error_detail: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisSummaryResponse(BaseModel):
    analysis_id: int
    upload_id: int
    status: str
    error_detail: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None
    file_count: int = 0
    technology_count: int = 0
    dependency_count: int = 0
    metric_count: int = 0
    warning_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AnalysisFileResponse(BaseModel):
    id: int
    relative_path: str
    file_name: str
    extension: str | None = None
    file_size: int
    lines_of_code: int | None = None
    language: str | None = None
    is_directory: bool = False

    model_config = ConfigDict(from_attributes=True)


class AnalysisTechnologyResponse(BaseModel):
    id: int
    name: str
    category: str
    evidence: str | None = None
    confidence: str = "high"

    model_config = ConfigDict(from_attributes=True)


class AnalysisDependencyResponse(BaseModel):
    id: int
    name: str
    version: str | None = None
    type: str
    source_files: list[str] = []
    ecosystem: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisMetricResponse(BaseModel):
    id: int
    key: str
    value: int | str | None = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisWarningResponse(BaseModel):
    id: int
    detector_name: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisListItem(BaseModel):
    id: int
    upload_id: int
    status: str
    error_detail: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
