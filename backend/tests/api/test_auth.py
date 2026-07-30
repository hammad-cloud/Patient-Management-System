"""Tests for authentication endpoints."""

from fastapi.testclient import TestClient

from app.core.config import get_settings


settings = get_settings()


def test_login_success(client: TestClient) -> None:
    """Admin can log in with valid credentials and receive a JWT."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.admin_email,
            "password": settings.admin_password,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_rejects_invalid_password(client: TestClient) -> None:
    """Login should fail for an incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.admin_email,
            "password": "wrong-password",
        },
    )
    assert response.status_code == 401


def test_logout_revokes_token(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Logout should blacklist the token so protected routes reject it."""
    logout = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert logout.status_code == 200
    assert "Signed out" in logout.json()["message"]

    blocked = client.get("/api/v1/patients/", headers=auth_headers)
    assert blocked.status_code == 401
