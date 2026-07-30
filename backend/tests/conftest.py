"""Shared pytest fixtures for API tests."""

from __future__ import annotations

import os

# Isolate tests from local PostgreSQL before any app module is imported.
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite://"

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.config import get_settings
from app.crud.user import ensure_admin_user
from app.db.base import Base
from app.main import app
from app.models import Doctor, Patient, Staff, TokenBlacklist, User  # noqa: F401

get_settings.cache_clear()
settings = get_settings()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide an isolated in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        class_=Session,
    )
    session = TestingSessionLocal()
    ensure_admin_user(session)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """HTTP client with DB dependency overridden to the test session."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    """Return Authorization headers for the seeded admin user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.admin_email,
            "password": settings.admin_password,
        },
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_doctor_payload() -> dict:
    """Valid doctor create payload used across CRUD tests."""
    return {
        "full_name": "Dr. Ahmed Khan",
        "specialization": "Cardiology",
        "email": "ahmed.khan@hospital.com",
        "phone": "03001112233",
        "salary": "150000.00",
    }


@pytest.fixture()
def created_doctor_id(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_doctor_payload: dict,
) -> int:
    """Create a doctor and return its ID for patient assignment tests."""
    response = client.post(
        "/api/v1/doctors/",
        json=sample_doctor_payload,
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    listed = client.get("/api/v1/doctors/", headers=auth_headers)
    assert listed.status_code == 200, listed.text
    return int(listed.json()["items"][0]["id"])


@pytest.fixture()
def sample_patient_payload(created_doctor_id: int) -> dict:
    """Valid patient create payload linked to a seeded doctor."""
    return {
        "full_name": "Ali Khan",
        "age": 35,
        "gender": "male",
        "status": "active",
        "phone": "03001234567",
        "email": "ali.khan@example.com",
        "address": "Lahore, Pakistan",
        "diseases": ["Diabetes", "Hypertension"],
        "medical_history": "Family history of heart disease",
        "doctor_id": created_doctor_id,
    }


@pytest.fixture()
def sample_staff_payload() -> dict:
    """Valid staff create payload used across CRUD tests."""
    return {
        "full_name": "Fatima Noor",
        "role": "Nurse",
        "shift": "morning",
        "email": "fatima.noor@hospital.com",
        "phone": "03005556677",
        "salary": "45000.00",
    }
