from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.integrations.ai.provider import AIProvider, LiteLLMProvider
from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.prompt_loader import PromptLoader
from app.modules.ai.service import AIService, DefaultAIService
from app.modules.auth import service as auth_service
from app.modules.uploads.quota import QuotaService
from app.storage.local import LocalStorageProvider

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return auth_service.get_current_user(db, token)


def get_storage_provider() -> LocalStorageProvider:
    return LocalStorageProvider(root=settings.UPLOAD_ROOT)


def get_quota_service() -> QuotaService:
    return QuotaService(settings)


def get_ai_provider() -> AIProvider:
    return LiteLLMProvider(
        model=settings.AI_MODEL,
        api_key=settings.AI_API_KEY,
        temperature=settings.AI_TEMPERATURE,
        max_tokens=settings.AI_MAX_TOKENS,
        timeout=settings.AI_TIMEOUT_SECONDS,
    )


def get_ai_service(provider: AIProvider = Depends(get_ai_provider)) -> AIService:
    return DefaultAIService(
        provider=provider,
        context_builder=ContextBuilder(),
        prompt_loader=PromptLoader(),
    )
