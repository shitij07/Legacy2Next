import os
import uuid

from app.storage.base import FileStorageResult, StorageProvider


class LocalStorageProvider(StorageProvider):
    def __init__(self, root: str):
        self._root = root

    def save(self, project_id: int, content: bytes, extension: str) -> FileStorageResult:
        project_dir = os.path.join(self._root, str(project_id), "files")
        os.makedirs(project_dir, exist_ok=True)

        stored_name = f"{uuid.uuid4().hex}{extension}"
        relative_path = os.path.join(str(project_id), "files", stored_name)
        full = os.path.join(self._root, relative_path)

        with open(full, "wb") as f:
            f.write(content)

        return FileStorageResult(
            stored_name=stored_name,
            relative_path=relative_path,
            file_size=len(content),
        )

    def delete(self, relative_path: str) -> None:
        full = self.full_path(relative_path)
        if os.path.exists(full):
            os.remove(full)

    def full_path(self, relative_path: str) -> str:
        return os.path.join(self._root, relative_path)

    def exists(self, relative_path: str) -> bool:
        return os.path.exists(self.full_path(relative_path))
