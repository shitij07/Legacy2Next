import math
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy.orm import Session, load_only

from app.models.comparison import Comparison

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


def create_comparison(db: Session, data: dict) -> Comparison:
    comparison = Comparison(**data)
    db.add(comparison)
    db.flush()
    db.refresh(comparison)
    return comparison


def get_comparison(db: Session, comparison_id: int) -> Comparison | None:
    return db.query(Comparison).filter(Comparison.id == comparison_id).first()


def delete_comparison(db: Session, comparison: Comparison) -> None:
    db.delete(comparison)
    db.flush()


def list_comparisons(
    db: Session,
    *,
    project_id: int,
    page: int = 1,
    size: int = 20,
) -> Page[Comparison]:
    query = db.query(Comparison).filter(Comparison.project_id == project_id)
    query = query.order_by(Comparison.created_at.desc())

    total = query.count()
    items = (
        query.options(load_only(Comparison.id, Comparison.project_id, Comparison.analysis_a_id, Comparison.analysis_b_id, Comparison.created_at))
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return Page(items=items, total=total, page=page, size=size)
