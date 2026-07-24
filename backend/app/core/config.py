"""Application settings loaded from environment variables / .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration."""

    app_name: str = "Patient Management System"
    # Default targets local PostgreSQL. Tests override with in-memory SQLite.
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/hospital_db"

    secret_key: str = "change-this-to-a-long-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    admin_email: str = "admin123@gmail.com"
    admin_password: str = "12345678"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def is_sqlite(self) -> bool:
        """Return True when the configured database is SQLite."""
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
