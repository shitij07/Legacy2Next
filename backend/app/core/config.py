from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Legacy2Next"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    DATABASE_ECHO: bool = False

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/legacy2next"

    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    UPLOAD_ROOT: str = "uploads"

    MAX_FILE_SIZE_MB: int = 50
    MAX_FILES_PER_REQUEST: int = 100
    MAX_REQUEST_SIZE_MB: int = 500
    ALLOWED_EXTENSIONS: list[str] = [
        ".zip", ".py", ".js", ".ts", ".java", ".cs", ".cpp", ".h",
        ".rb", ".go", ".rs", ".sql", ".xml", ".json", ".yaml", ".yml",
        ".md", ".txt", ".cfg", ".ini", ".properties",
        ".css", ".html", ".htm", ".php", ".swift", ".kt", ".scala",
        ".sh", ".bat", ".ps1", ".env", ".toml",
    ]
    ALLOWED_MIME_TYPES: list[str] = [
        "application/zip", "application/x-zip-compressed",
        "text/plain", "text/x-python", "text/javascript",
        "application/javascript", "text/typescript", "text/x-java",
        "text/x-csrc", "text/x-c++src", "text/x-ruby", "text/x-go",
        "text/x-rust", "text/x-sql", "text/xml", "application/json",
        "text/yaml", "text/markdown", "text/x-java-source",
        "text/x-php", "text/x-swift", "text/x-kotlin",
        "text/x-sh", "text/x-msdos-batch",
    ]

    MAX_PROJECT_STORAGE_GB: int = 5

    MAX_PAGE_SIZE_SUBRESOURCE: int = 200
    MAX_PAGE_SIZE_LIST: int = 100
    DEFAULT_PAGE_SIZE_SUBRESOURCE: int = 50
    DEFAULT_PAGE_SIZE_LIST: int = 20
    SLOW_SERVICE_THRESHOLD_MS: int = 1000

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    AI_ENABLED: bool = True
    AI_PROVIDER: str = "litellm"
    AI_MODEL: str = "gpt-4o-mini"
    AI_API_KEY: str = ""
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 2048
    AI_TIMEOUT_SECONDS: int = 60

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        if not self.DEBUG and self.SECRET_KEY == "change-me":
            raise ValueError(
                "SECRET_KEY must be changed from the default value in production"
            )
        return self

    class Config:
        env_file = ".env"


settings = Settings()
