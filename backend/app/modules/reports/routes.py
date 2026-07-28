from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.reports.schemas import (
    ReportCreate,
    ReportListResponse,
    ReportResponse,
)
from app.modules.reports import service as reports_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=201)
def create_report(
    body: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return reports_service.generate_report(
        db=db,
        user_id=current_user.id,
        project_id=body.project_id,
        analysis_id=body.analysis_id,
        title=body.title,
        report_format=body.format,
    )


@router.get("", response_model=ReportListResponse)
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    project_id: int = Query(..., ge=1),
    analysis_id: int | None = Query(None, ge=1),
    status: str | None = None,
    format: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE_LIST, ge=1, le=settings.MAX_PAGE_SIZE_LIST),
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    return reports_service.list_reports(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        analysis_id=analysis_id,
        status=status,
        format=format,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return reports_service.get_report(
        db=db,
        user_id=current_user.id,
        report_id=report_id,
    )


@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return reports_service.delete_report(
        db=db,
        user_id=current_user.id,
        report_id=report_id,
    )
