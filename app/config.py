"""
Environment-based configuration. No hardcoded secrets.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ApexNeural Tracking"
    environment: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/tracking"

    # Click redirect: after GET /t/{tracking_id}, send user here (no path = homepage)
    redirect_base_url: str = "https://apexneural.com"


def get_settings() -> Settings:
    return Settings()
