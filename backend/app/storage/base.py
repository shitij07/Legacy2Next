from abc import ABC, abstractmethod

from typing_extensions import TypedDict


class FileStorageResult(TypedDict):
    stored_name: str
    relative_path: str
    file_size: int


class StorageProvider(ABC):
    @abstractmethod
    def save(self, project_id: int, content: bytes, extension: str) -> FileStorageResult:
        ...

    @abstractmethod
    def delete(self, relative_path: str) -> None:
        ...

    @abstractmethod
    def full_path(self, relative_path: str) -> str:
        ...

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        ...
