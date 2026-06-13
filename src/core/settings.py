from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # ----- پایگاه داده -----
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/teos"
    DATABASE_SYNC_URL: str = "postgresql://user:password@localhost:5432/teos"

    # ----- Redis -----
    REDIS_URL: str = "redis://localhost:6379/0"

    # ----- Elasticsearch -----
    ES_HOSTS: str = "http://localhost:9200"

    # ----- Security -----
    SECRET_KEY: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ----- Telegram -----
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: Optional[str] = None

    # ----- AI -----
    AI_BACKEND: str = "openai"
    AI_MODEL: str = "gpt-4o-mini"
    AI_API_KEY: Optional[str] = None
    AI_MAX_TOKENS: int = 1024
    AI_TEMPERATURE: float = 0.7

    # ----- Storage -----
    UPLOAD_DIR: str = "./uploads"
    BACKUP_DIR: str = "./backups"

    # ----- General -----
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
