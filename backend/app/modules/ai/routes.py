from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.ai.schemas import GenerationResponse, ModuleExplanationRequest
from app.modules.ai.service import AIService
from app.core.dependencies import get_ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analysis/{analysis_id}/summary", response_model=GenerationResponse)
def generate_summary(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    return ai_service.generate_summary(db=db, user_id=current_user.id, analysis_id=analysis_id)


@router.post("/analysis/{analysis_id}/file/{file_id}/explain", response_model=GenerationResponse)
def generate_file_explanation(
    analysis_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    return ai_service.generate_file_explanation(db=db, user_id=current_user.id, analysis_id=analysis_id, file_id=file_id)


@router.post("/analysis/{analysis_id}/module", response_model=GenerationResponse)
def generate_module_explanation(
    analysis_id: int,
    body: ModuleExplanationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    return ai_service.generate_module_explanation(db=db, user_id=current_user.id, analysis_id=analysis_id, module_path=body.module_path)


@router.post("/analysis/{analysis_id}/architecture", response_model=GenerationResponse)
def generate_architecture(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    return ai_service.generate_architecture(db=db, user_id=current_user.id, analysis_id=analysis_id)


@router.post("/analysis/{analysis_id}/technical-debt", response_model=GenerationResponse)
def generate_technical_debt(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    return ai_service.generate_technical_debt(db=db, user_id=current_user.id, analysis_id=analysis_id)


@router.post("/analysis/{analysis_id}/modernization", response_model=GenerationResponse)
def generate_modernization(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    return ai_service.generate_modernization(db=db, user_id=current_user.id, analysis_id=analysis_id)
