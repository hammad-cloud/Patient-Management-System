"""Patient API endpoints."""

from __future__ import annotations

from typing import Any

from api.client import api_request


def list_patients(
    *,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    gender: str | None = None,
    status: str | None = None,
    doctor_id: int | None = None,
) -> dict[str, Any]:
    """Fetch a paginated patient list."""
    return api_request(
        "GET",
        "/patients/",
        params={
            "page": page,
            "limit": limit,
            "search": search,
            "gender": gender,
            "status": status,
            "doctor_id": doctor_id,
        },
        auth=True,
    )


def get_patient(patient_id: int) -> dict[str, Any]:
    """Fetch a single patient by ID."""
    return api_request("GET", f"/patients/{patient_id}", auth=True)


def create_patient(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a new patient."""
    return api_request("POST", "/patients/", json=payload, auth=True)


def update_patient(patient_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update an existing patient (partial payload allowed)."""
    return api_request("PATCH", f"/patients/{patient_id}", json=payload, auth=True)


def delete_patient(patient_id: int) -> dict[str, Any]:
    """Permanently delete a patient."""
    return api_request("DELETE", f"/patients/{patient_id}", auth=True)
