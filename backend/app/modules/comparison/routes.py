from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.comparison.schemas import (
    ComparisonCreate,
    ComparisonListResponse,
    ComparisonResponse,
)
from app.modules.comparison import service as comparison_service

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.post("", response_model=ComparisonResponse, status_code=201)
def create_comparison(
    body: ComparisonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return comparison_service.generate_comparison(
        db=db,
        user_id=current_user.id,
        project_id=body.project_id,
        analysis_a_id=body.analysis_a_id,
        analysis_b_id=body.analysis_b_id,
    )


@router.get("/project/{project_id}", response_model=ComparisonListResponse)
def list_comparisons(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE_LIST, ge=1, le=settings.MAX_PAGE_SIZE_LIST),
):
    return comparison_service.list_comparisons(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        page=page,
        size=size,
    )


@router.get("/{comparison_id}", response_model=ComparisonResponse)
def get_comparison(
    comparison_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return comparison_service.get_comparison(
        db=db,
        user_id=current_user.id,
        comparison_id=comparison_id,
    )


@router.delete("/{comparison_id}", status_code=204)
def delete_comparison(
    comparison_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return comparison_service.delete_comparison(
        db=db,
        user_id=current_user.id,
        comparison_id=comparison_id,
    )
