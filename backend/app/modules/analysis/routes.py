from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.analysis import query_service
from app.modules.analysis import service as analysis_service
from app.modules.analysis.schemas import (
    AnalysisDependencyResponse,
    AnalysisFileResponse,
    AnalysisListItem,
    AnalysisMetricResponse,
    AnalysisResponse,
    AnalysisSummaryResponse,
    AnalysisTechnologyResponse,
    AnalysisWarningResponse,
    PaginatedResponse,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{upload_id}", response_model=AnalysisResponse, status_code=201)
def run_analysis(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return analysis_service.run_analysis(
        db=db,
        user_id=current_user.id,
        upload_id=upload_id,
    )


@router.get("/project/{project_id}", response_model=PaginatedResponse[AnalysisListItem])
def list_project_analyses(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    return query_service.list_project_analyses(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/upload/{upload_id}", response_model=PaginatedResponse[AnalysisListItem])
def list_upload_analyses(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    return query_service.list_upload_analyses(
        db=db,
        user_id=current_user.id,
        upload_id=upload_id,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/{analysis_id}", response_model=AnalysisSummaryResponse)
def get_analysis_summary(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return query_service.get_analysis_summary(
        db=db,
        user_id=current_user.id,
        analysis_id=analysis_id,
    )


@router.get("/{analysis_id}/files", response_model=PaginatedResponse[AnalysisFileResponse])
def get_analysis_files(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    extension: str | None = None,
    language: str | None = None,
    is_directory: bool | None = None,
    search: str | None = Query(None, min_length=2),
    sort_by: str = "relative_path",
    sort_dir: str = "asc",
):
    return query_service.get_analysis_files(
        db=db,
        user_id=current_user.id,
        analysis_id=analysis_id,
        page=page,
        size=size,
        extension=extension,
        language=language,
        is_directory=is_directory,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/{analysis_id}/technologies", response_model=list[AnalysisTechnologyResponse])
def get_analysis_technologies(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return query_service.get_analysis_technologies(
        db=db,
        user_id=current_user.id,
        analysis_id=analysis_id,
    )


@router.get("/{analysis_id}/dependencies", response_model=PaginatedResponse[AnalysisDependencyResponse])
def get_analysis_dependencies(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    ecosystem: str | None = None,
    type: str | None = None,
    search: str | None = Query(None, min_length=2),
    sort_by: str = "name",
    sort_dir: str = "asc",
):
    return query_service.get_analysis_dependencies(
        db=db,
        user_id=current_user.id,
        analysis_id=analysis_id,
        page=page,
        size=size,
        ecosystem=ecosystem,
        type=type,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/{analysis_id}/metrics", response_model=list[AnalysisMetricResponse])
def get_analysis_metrics(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return query_service.get_analysis_metrics(
        db=db,
        user_id=current_user.id,
        analysis_id=analysis_id,
    )


@router.get("/{analysis_id}/warnings", response_model=PaginatedResponse[AnalysisWarningResponse])
def get_analysis_warnings(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    detector_name: str | None = None,
    search: str | None = Query(None, min_length=2),
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    return query_service.get_analysis_warnings(
        db=db,
        user_id=current_user.id,
        analysis_id=analysis_id,
        page=page,
        size=size,
        detector_name=detector_name,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
