import math
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.models.report import Report, ReportFormat, ReportStatus

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        return max(1, math.ceil(self.total / self.size))


_REPORT_SORT_FIELDS = {"created_at", "title", "format", "status"}


def _validate_sort(allowed: set[str], sort_by: str) -> str:
    if sort_by not in allowed:
        return next(iter(allowed))
    return sort_by


def create_report(db: Session, data: dict) -> Report:
    report = Report(**data)
    db.add(report)
    db.flush()
    db.refresh(report)
    return report


def get_report(db: Session, report_id: int) -> Report | None:
    return db.query(Report).filter(Report.id == report_id).first()


def update_report(db: Session, report: Report, data: dict) -> Report:
    for key, value in data.items():
        setattr(report, key, value)
    db.flush()
    db.refresh(report)
    return report


def delete_report(db: Session, report: Report) -> None:
    db.delete(report)
    db.flush()


def list_reports(
    db: Session,
    *,
    project_id: int | None = None,
    analysis_id: int | None = None,
    status: ReportStatus | None = None,
    format: ReportFormat | None = None,
    page: int = 1,
    size: int = 20,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> Page[Report]:
    query = db.query(Report)

    if project_id is not None:
        query = query.filter(Report.project_id == project_id)
    if analysis_id is not None:
        query = query.filter(Report.analysis_id == analysis_id)
    if status is not None:
        query = query.filter(Report.status == status)
    if format is not None:
        query = query.filter(Report.format == format)

    sort_by = _validate_sort(_REPORT_SORT_FIELDS, sort_by)
    sort_col = getattr(Report, sort_by)
    if sort_dir == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return Page(items=items, total=total, page=page, size=size)
