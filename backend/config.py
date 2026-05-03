"""
config.py
---------
All configuration loaded from environment variables.
Pydantic-settings validates and coerces types automatically.

Create a .env file in the repo root for local dev:

    DATABASE_URL=postgresql+asyncpg://cropsense:cropsense@localhost:5432/cropsense
    ML_SERVICE_URL=http://localhost:8000
    BACKEND_PORT=8001
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Postgres — asyncpg driver required
    database_url: str = "postgresql+asyncpg://cropsense:cropsense@localhost:5432/cropsense"

    # ML microservice base URL (Phase 2 service)
    ml_service_url: str = "http://localhost:8000"

    # Backend server port
    backend_port: int = 8001

    # CORS
    cors_origins: str = "*"

    # HTTP client timeout when calling ML service (seconds)
    ml_timeout: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()