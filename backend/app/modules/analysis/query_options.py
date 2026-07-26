import math
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy.orm import Query

T = TypeVar("T")


@dataclass(frozen=True)
class QueryOptions:
    page: int = 1
    size: int = 50
    sort_by: str | None = None
    sort_dir: str = "asc"


@dataclass(frozen=True)
class FileFilter:
    extension: str | None = None
    language: str | None = None
    is_directory: bool | None = None
    search: str | None = None


@dataclass(frozen=True)
class DependencyFilter:
    ecosystem: str | None = None
    type: str | None = None
    search: str | None = None


@dataclass(frozen=True)
class WarningFilter:
    detector_name: str | None = None
    search: str | None = None


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        return max(1, math.ceil(self.total / self.size))


def apply_sort(query: Query, allowed_fields: dict[str, object], opts: QueryOptions) -> Query:
    column = allowed_fields.get(opts.sort_by) if opts.sort_by else None
    if column is None:
        column = next(iter(allowed_fields.values()))
    if opts.sort_dir == "desc":
        return query.order_by(column.desc())
    return query.order_by(column.asc())
