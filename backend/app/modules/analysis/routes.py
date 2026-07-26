from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.analysis import service as analysis_service
from app.modules.analysis.schemas import AnalysisResponse

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
