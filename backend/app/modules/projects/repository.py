from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.project import Project


def get_project_by_id(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def list_projects_by_owner(
    db: Session, user_id: int, *, offset: int = 0, limit: int = 20
) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def count_projects_by_owner(db: Session, user_id: int) -> int:
    return (
        db.query(func.count(Project.id))
        .filter(Project.user_id == user_id)
        .scalar()
        or 0
    )


def create_project(db: Session, project: Project) -> Project:
    db.add(project)
    db.flush()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project) -> Project:
    db.flush()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.flush()
