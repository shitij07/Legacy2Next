from datetime import datetime

from pydantic import BaseModel


class GeneralSection(BaseModel):
    analysis_id: int
    upload_id: int
    status: str
    error_detail: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None


class LanguageCount(BaseModel):
    language: str
    count: int


class ExtensionCount(BaseModel):
    extension: str
    count: int


class DirectorySize(BaseModel):
    relative_path: str
    file_size: int


class FilesSection(BaseModel):
    total_files: int = 0
    total_directories: int = 0
    language_distribution: list[LanguageCount] = []
    extension_distribution: list[ExtensionCount] = []
    largest_directories: list[DirectorySize] = []


class CategoryCount(BaseModel):
    category: str
    count: int


class ConfidenceCount(BaseModel):
    confidence: str
    count: int


class TechnologiesSection(BaseModel):
    total_technologies: int = 0
    category_distribution: list[CategoryCount] = []
    confidence_distribution: list[ConfidenceCount] = []
    primary_frameworks: list[str] = []


class EcosystemBreakdown(BaseModel):
    ecosystem: str
    count: int


class TopPackage(BaseModel):
    name: str
    version: str | None = None
    ecosystem: str | None = None


class DependenciesSection(BaseModel):
    total_dependencies: int = 0
    direct_count: int = 0
    transitive_count: int = 0
    ecosystem_breakdown: list[EcosystemBreakdown] = []
    top_packages: list[TopPackage] = []


class DetectorCount(BaseModel):
    detector_name: str
    count: int


class WarningsSection(BaseModel):
    total_warnings: int = 0
    detector_breakdown: list[DetectorCount] = []


class MetricsSection(BaseModel):
    total_metrics: int = 0
    project_total_files: int | None = None
    project_total_file_size: int | None = None
    language_count: int | None = None
    primary_language: str | None = None
    framework_count: int | None = None
    dependency_count: int | None = None
    manifest_count: int | None = None


class DashboardResponse(BaseModel):
    general: GeneralSection
    files: FilesSection
    technologies: TechnologiesSection
    dependencies: DependenciesSection
    warnings: WarningsSection
    metrics: MetricsSection
