"""Database engine, session factory, and session dependency."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
    """Enable foreign-key enforcement for SQLite connections."""
    if not settings.is_sqlite:
        return
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Prepare application data on startup.

    - SQLite (local/dev fallback): create/repair schema automatically.
    - PostgreSQL (primary): schema is managed by Alembic migrations.
    - Always seed the default admin user (skipped under pytest).
    """
    # Tests provide their own isolated DB via fixtures.
    if os.getenv("TESTING") == "1":
        return

    from app.crud.user import ensure_admin_user
    from app.db.base import Base
    from app.models import Doctor, Patient, Staff, TokenBlacklist, User  # noqa: F401

    if settings.is_sqlite:
        Base.metadata.create_all(bind=engine)
        _ensure_sqlite_patient_columns()
        _ensure_sqlite_staff_columns()

    db = SessionLocal()
    try:
        ensure_admin_user(db)
    finally:
        db.close()


def _ensure_sqlite_patient_columns() -> None:
    """Add missing patient columns to existing SQLite databases."""
    from sqlalchemy import text

    if not settings.is_sqlite:
        return

    with engine.begin() as connection:
        rows = connection.execute(text("PRAGMA table_info(patients)")).fetchall()
        column_names = {row[1] for row in rows}

        if "diseases" not in column_names:
            connection.execute(
                text("ALTER TABLE patients ADD COLUMN diseases JSON NOT NULL DEFAULT '[]'")
            )

        if "status" not in column_names:
            connection.execute(
                text(
                    "ALTER TABLE patients ADD COLUMN status VARCHAR(20) "
                    "NOT NULL DEFAULT 'active'"
                )
            )

        if "doctor_id" not in column_names:
            connection.execute(text("ALTER TABLE patients ADD COLUMN doctor_id INTEGER"))


def _ensure_sqlite_staff_columns() -> None:
    """Add missing staff email/phone columns to existing SQLite databases."""
    from sqlalchemy import text

    if not settings.is_sqlite:
        return

    with engine.begin() as connection:
        table_exists = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='staff'")
        ).fetchone()
        if table_exists is None:
            return

        rows = connection.execute(text("PRAGMA table_info(staff)")).fetchall()
        column_names = {row[1] for row in rows}

        if "email" not in column_names:
            connection.execute(text("ALTER TABLE staff ADD COLUMN email VARCHAR(255)"))
        if "phone" not in column_names:
            connection.execute(text("ALTER TABLE staff ADD COLUMN phone VARCHAR(20)"))

        connection.execute(
            text(
                "UPDATE staff SET email = 'staff' || id || '@local.invalid' "
                "WHERE email IS NULL OR TRIM(email) = ''"
            )
        )
        connection.execute(
            text(
                "UPDATE staff SET phone = printf('0300%07d', id) "
                "WHERE phone IS NULL OR TRIM(phone) = ''"
            )
        )
