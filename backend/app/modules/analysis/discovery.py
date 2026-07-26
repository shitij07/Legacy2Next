import logging
import os
import time
from itertools import count
from pathlib import Path

from app.modules.analysis.ignore_rules import IgnoreRules
from app.modules.analysis.types import (
    DirectoryNode,
    DiscoveryContext,
    DiscoveryStats,
    FileGraph,
    FileNode,
)

logger = logging.getLogger(__name__)


class DiscoveryException(Exception):
    pass


class DiscoveryEngine:

    def discover(
        self,
        *,
        root_path: Path,
        upload_id: int,
        project_id: int,
        ignore_rules: IgnoreRules | None = None,
    ) -> DiscoveryContext:
        if ignore_rules is None:
            ignore_rules = IgnoreRules.defaults()

        if not root_path.exists():
            raise DiscoveryException(f"Root path does not exist: {root_path}")
        if not root_path.is_dir():
            raise DiscoveryException(f"Root path is not a directory: {root_path}")

        start = time.perf_counter()
        files: list[FileNode] = []
        directories: list[DirectoryNode] = []
        by_path: dict[str, FileNode | DirectoryNode] = {}
        tree: dict[str, list[str]] = {}
        ignored = 0
        _ids = count(1)

        root_rel = "."
        dir_node = DirectoryNode(
            id=next(_ids),
            relative_path=root_rel,
            directory_name=root_path.name,
        )
        directories.append(dir_node)
        by_path[root_rel] = dir_node

        def _onerror(err: OSError) -> None:
            logger.warning("Cannot access %s: %s", err.filename, err.strerror)

        for dirpath, dirnames, filenames in os.walk(
            root_path, topdown=True, onerror=_onerror,
        ):
            rel_dir = Path(dirpath).relative_to(root_path).as_posix()

            dirnames.sort()
            filenames.sort()
            children: list[str] = []

            for filename in filenames:
                file_rel = f"{rel_dir}/{filename}" if rel_dir != "." else filename
                if ignore_rules.should_ignore(file_rel, is_dir=False):
                    ignored += 1
                    continue

                full = Path(dirpath) / filename
                try:
                    stat = full.stat()
                except OSError:
                    logger.warning("Cannot stat file: %s", file_rel)
                    ignored += 1
                    continue

                ext = full.suffix
                node = FileNode(
                    id=next(_ids),
                    relative_path=file_rel,
                    file_name=filename,
                    extension=ext,
                    file_size=stat.st_size,
                )
                files.append(node)
                by_path[file_rel] = node
                children.append(file_rel)

            filtered: list[str] = []
            for dirname in dirnames:
                dir_rel = f"{rel_dir}/{dirname}" if rel_dir != "." else dirname
                if ignore_rules.should_ignore(dir_rel, is_dir=True):
                    ignored += 1
                    continue
                filtered.append(dirname)
                node = DirectoryNode(
                    id=next(_ids),
                    relative_path=dir_rel,
                    directory_name=dirname,
                )
                directories.append(node)
                by_path[dir_rel] = node
                children.append(dir_rel)

            dirnames[:] = filtered
            tree[rel_dir] = children

        duration_ms = int((time.perf_counter() - start) * 1000)
        file_graph = FileGraph(
            files=files,
            directories=directories,
            by_path=by_path,
            tree=tree,
        )
        stats = DiscoveryStats(
            total_files=len(files),
            total_directories=len(directories),
            ignored_entries=ignored,
            duration_ms=duration_ms,
        )
        return DiscoveryContext(
            upload_id=upload_id,
            project_id=project_id,
            root_path=root_path.resolve(),
            file_graph=file_graph,
            stats=stats,
        )
