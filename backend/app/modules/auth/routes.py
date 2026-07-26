from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = service.register(db, body)
    return user


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return service.login(db, body)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
