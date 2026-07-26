from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth import service as auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return auth_service.get_current_user(db, token)
