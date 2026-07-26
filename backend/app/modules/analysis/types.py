from dataclasses import dataclass, field
from pathlib import Path


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
