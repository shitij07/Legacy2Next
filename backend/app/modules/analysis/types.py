from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DetectedTechnology:
    name: str
    category: str
    evidence: str | None = None
    confidence: str = "high"


@dataclass(frozen=True)
class DetectedDependency:
    name: str
    version: str | None = None
    type: str = "library"
    source_files: tuple[str, ...] = ()
    ecosystem: str | None = None
    category: str = "runtime"


@dataclass(frozen=True)
class DetectedMetric:
    key: str
    value: int | str


@dataclass(frozen=True)
class DetectedFile:
    relative_path: str
    file_name: str
    extension: str
    file_size: int
    language: str | None = None


@dataclass(frozen=True)
class DetectorWarning:
    detector_name: str
    message: str


@dataclass(frozen=True)
class DetectorResult:
    detector_name: str
    technologies: tuple[DetectedTechnology, ...] = ()
    files: tuple[DetectedFile, ...] = ()
    dependencies: tuple[DetectedDependency, ...] = ()
    metrics: tuple[DetectedMetric, ...] = ()
    warnings: tuple[DetectorWarning, ...] = ()
    error: str | None = None


@dataclass
class AnalysisResults:
    results: list[DetectorResult]
    start_time: float
    end_time: float | None = None

    @property
    def all_technologies(self) -> list[DetectedTechnology]:
        return [t for r in self.results for t in r.technologies]

    @property
    def all_files(self) -> list[DetectedFile]:
        return [f for r in self.results for f in r.files]

    @property
    def all_dependencies(self) -> list[DetectedDependency]:
        return [d for r in self.results for d in r.dependencies]

    @property
    def all_metrics(self) -> list[DetectedMetric]:
        return [m for r in self.results for m in r.metrics]

    @property
    def errors(self) -> list[str]:
        return [r.error for r in self.results if r.error is not None]

    @property
    def has_errors(self) -> bool:
        return any(r.error is not None for r in self.results)


@dataclass(frozen=True)
class FileNode:
    id: int
    relative_path: str
    file_name: str
    extension: str
    file_size: int
    is_directory: bool = False


@dataclass(frozen=True)
class DirectoryNode:
    id: int
    relative_path: str
    directory_name: str
    is_directory: bool = True


@dataclass(frozen=True)
class FileGraph:
    files: list[FileNode]
    directories: list[DirectoryNode]
    by_path: dict[str, FileNode | DirectoryNode] = field(repr=False)
    tree: dict[str, list[str]] = field(repr=False)

    def get_node(self, path: str) -> FileNode | DirectoryNode | None:
        return self.by_path.get(path)

    def get_children(self, path: str) -> list[str]:
        return self.tree.get(path, [])

    def find_files_by_name(self, name: str) -> list[FileNode]:
        return [f for f in self.files if f.file_name == name]


@dataclass(frozen=True)
class DiscoveryStats:
    total_files: int
    total_directories: int
    ignored_entries: int
    duration_ms: int


@dataclass(frozen=True)
class DiscoveryContext:
    upload_id: int
    project_id: int
    root_path: Path
    file_graph: FileGraph
    stats: DiscoveryStats
