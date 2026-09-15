from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application configuration.

    Values are loaded from environment variables and .env.
    """

    # =========================================================
    # Application
    # =========================================================

    APP_NAME: str = "Orion AI System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # =========================================================
    # API
    # =========================================================

    API_PREFIX: str = "/api"

    # =========================================================
    # Database
    # =========================================================

    DATABASE_URL: str = (
        "postgresql+asyncpg://"
        "postgres:Application123"
        "@localhost:5432/orion_ai"
    )

    # =========================================================
    # JWT
    # =========================================================

    JWT_SECRET_KEY: str = (
        "D6--RGdVH0z24EHtJJQgbx-vtCbkXzaj3L2N5smouHlkyF5AjqYq"
        "Br_iKT0C0fdi5vu_113vhycI_Y8wIvlJGQ"
    )

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =========================================================
    # Password hashing
    # =========================================================

    PASSWORD_HASH_ALGORITHM: str = "bcrypt"

    # =========================================================
    # CORS
    # =========================================================

    FRONTEND_URL: str = "http://localhost:3000"

    # =========================================================
    # Pydantic Settings
    # =========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Return the cached application settings instance.
    """

    return Settings()


# IMPORTANT:
#
# Do NOT put a comma here.
#
# Wrong:
#     settings = get_settings(),
#
# That creates:
#     (Settings(...),)
#
# which is a tuple.
#
# Correct:
settings = get_settings()