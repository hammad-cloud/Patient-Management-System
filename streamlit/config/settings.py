"""Central configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Streamlit frontend settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Patient Management System"
    api_base_url: str = "http://127.0.0.1:8000/api/v1"
    request_timeout_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
