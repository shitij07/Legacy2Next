from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Legacy2Next"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/legacy2next"

    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 104_857_600

    class Config:
        env_file = ".env"


settings = Settings()
