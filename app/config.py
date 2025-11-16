from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    MONGODB_URL: str
    REDIS_URL: str

    # Storage
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_SECURE: bool = False  # default false unless explicitly set

    # LLM
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # App Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE: int = 104857600
    ALLOWED_EXTENSIONS: str = ".txt,.pdf,.md"

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "allow"   # <-- IMPORTANT: allow extra fields if needed
        

settings = Settings()
