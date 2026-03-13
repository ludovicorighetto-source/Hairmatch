from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────────────────────────
    APP_NAME: str = "HairMatch"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    DEV_MODE: bool = False  # When True, bypasses Supabase – never use in production

    # ─── Database ─────────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://hairmatch:hairmatch_secret@localhost:5432/hairmatch_db"

    # ─── Redis ────────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://:redis_secret@localhost:6379/0"

    # ─── Supabase ─────────────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # ─── JWT ──────────────────────────────────────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── CORS ─────────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ─── Rate Limiting ────────────────────────────────────────────────────────────
    RATE_LIMIT_LOGIN: str = "10/15minutes"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def refresh_token_expire_seconds(self) -> int:
        return self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
