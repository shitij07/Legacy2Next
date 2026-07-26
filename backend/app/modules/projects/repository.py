from sqlalchemy.orm import Session

from app.models.project import Project


def get_project_by_id(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def list_projects_by_owner(db: Session, user_id: int) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def create_project(db: Session, project: Project) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project) -> Project:
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
