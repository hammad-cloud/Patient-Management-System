"""Authentication API endpoints."""

from __future__ import annotations

from typing import Any

from api.client import api_request


def login(email: str, password: str) -> dict[str, Any]:
    """Authenticate and return token payload."""
    return api_request(
        "POST",
        "/auth/login",
        json={"email": email, "password": password},
        auth=False,
    )


def logout() -> dict[str, Any] | None:
    """Revoke the current access token on the backend."""
    return api_request("POST", "/auth/logout", auth=True)
