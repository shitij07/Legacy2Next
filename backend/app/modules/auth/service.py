from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.models.user import User
from app.modules.auth import repository
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse


def register(db: Session, request: RegisterRequest) -> User:
    existing = repository.get_by_email(db, request.email)
    if existing:
        raise ConflictException(code="EMAIL_EXISTS", message="Email already registered")
    data = {
        "email": request.email,
        "password_hash": hash_password(request.password),
        "name": request.name,
    }
    user = repository.create(db, data)
    db.commit()
    return user


def login(db: Session, request: LoginRequest) -> TokenResponse:
    user = repository.get_by_email(db, request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise UnauthorizedException(message="Invalid email or password")
    token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=token)


def get_current_user(db: Session, token: str) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(message="Invalid or expired token")
    user = repository.get_by_id(db, int(user_id))
    if user is None:
        raise UnauthorizedException(message="Invalid or expired token")
    return user
