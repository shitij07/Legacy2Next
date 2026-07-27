from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.projects import service
from app.modules.projects.schemas import (
    PaginatedProjectListResponse,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    body: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_project(db, current_user.id, body)


@router.get("", response_model=PaginatedProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE_LIST, ge=1, le=settings.MAX_PAGE_SIZE_LIST),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_projects(db, current_user.id, page=page, size=size)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_project(db, current_user.id, project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    body: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_project(db, current_user.id, project_id, body)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete_project(db, current_user.id, project_id)
