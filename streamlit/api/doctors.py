"""Doctor API endpoints."""

from __future__ import annotations

from typing import Any

from api.client import api_request


def list_doctors(
    *,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    specialization: str | None = None,
) -> dict[str, Any]:
    """Fetch a paginated doctor list."""
    return api_request(
        "GET",
        "/doctors/",
        params={
            "page": page,
            "limit": limit,
            "search": search,
            "specialization": specialization,
        },
        auth=True,
    )


def get_doctor(doctor_id: int) -> dict[str, Any]:
    """Fetch a single doctor by ID."""
    return api_request("GET", f"/doctors/{doctor_id}", auth=True)


def create_doctor(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a new doctor."""
    return api_request("POST", "/doctors/", json=payload, auth=True)


def update_doctor(doctor_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update an existing doctor."""
    return api_request("PUT", f"/doctors/{doctor_id}", json=payload, auth=True)


def delete_doctor(doctor_id: int) -> dict[str, Any]:
    """Permanently delete a doctor."""
    return api_request("DELETE", f"/doctors/{doctor_id}", auth=True)
