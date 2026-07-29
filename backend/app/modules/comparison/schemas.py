from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

T = TypeVar("T")


class ComparisonCreate(BaseModel):
    project_id: int = Field(..., ge=1)
    analysis_a_id: int = Field(..., ge=1)
    analysis_b_id: int = Field(..., ge=1)


class MetricDiff(BaseModel):
    key: str
    a_value: int | str | None = None
    b_value: int | str | None = None
    abs_diff: int | None = None
    pct_diff: float | None = None


class MetricsComparison(BaseModel):
    loc: MetricDiff | None = None
    file_count: MetricDiff | None = None
    dependency_count: MetricDiff | None = None
    technology_count: MetricDiff | None = None
    warning_count: MetricDiff | None = None


class TechnologyComparison(BaseModel):
    added: list[dict] = []
    removed: list[dict] = []
    common: list[dict] = []
    version_changes: list[dict] = []


class DependencyComparison(BaseModel):
    added: list[dict] = []
    removed: list[dict] = []
    updated: list[dict] = []


class FileComparison(BaseModel):
    added: list[dict] = []
    removed: list[dict] = []
    modified: list[dict] = []
    total_a: int = 0
    total_b: int = 0


class WarningComparison(BaseModel):
    added: list[dict] = []
    resolved: list[dict] = []
    persistent: list[dict] = []
    delta: int = 0


class ComparisonData(BaseModel):
    technologies: TechnologyComparison = TechnologyComparison()
    dependencies: DependencyComparison = DependencyComparison()
    files: FileComparison = FileComparison()
    warnings: WarningComparison = WarningComparison()
    metrics: MetricsComparison = MetricsComparison()


class ComparisonResponse(BaseModel):
    id: int
    project_id: int
    analysis_a_id: int
    analysis_b_id: int
    summary: str | None = None
    comparison_data: ComparisonData | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComparisonSummary(BaseModel):
    id: int
    project_id: int
    analysis_a_id: int
    analysis_b_id: int
    summary: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComparisonListResponse(BaseModel):
    items: list[ComparisonSummary]
    total: int
    page: int
    size: int
    pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
