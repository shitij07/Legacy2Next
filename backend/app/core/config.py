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

    class Config:
        env_file = ".env"


settings = Settings()
