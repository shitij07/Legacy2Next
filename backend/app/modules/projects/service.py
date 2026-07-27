import math

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ValidationException
from app.models.project import Project
from app.modules.projects import repository
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate


def _paginated_response(items: list, total: int, page: int, size: int) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": max(1, math.ceil(total / size)) if size > 0 else 1,
    }


def _get_owned_project(db: Session, user_id: int, project_id: int) -> Project:
    project = repository.get_project_by_id(db, project_id)
    if project is None or project.user_id != user_id:
        raise NotFoundException("Project")
    return project


def create_project(db: Session, user_id: int, request: ProjectCreate) -> Project:
    kwargs: dict = {"user_id": user_id, "name": request.name}
    if request.description is not None:
        kwargs["description"] = request.description
    project = Project(**kwargs)
    project = repository.create_project(db, project)
    db.commit()
    return project


def get_project(db: Session, user_id: int, project_id: int) -> Project:
    return _get_owned_project(db, user_id, project_id)


def list_projects(
    db: Session, user_id: int, *, page: int = 1, size: int = 20
) -> dict:
    offset = (page - 1) * size
    items = repository.list_projects_by_owner(db, user_id, offset=offset, limit=size)
    total = repository.count_projects_by_owner(db, user_id)
    return _paginated_response(items, total, page, size)


def update_project(
    db: Session, user_id: int, project_id: int, request: ProjectUpdate
) -> Project:
    project = _get_owned_project(db, user_id, project_id)
    updates = request.model_dump(exclude_unset=True)
    if not updates:
        raise ValidationException("At least one field must be provided")
    for field, value in updates.items():
        setattr(project, field, value)
    project = repository.update_project(db, project)
    db.commit()
    return project


def delete_project(db: Session, user_id: int, project_id: int) -> None:
    project = _get_owned_project(db, user_id, project_id)
    repository.delete_project(db, project)
    db.commit()
