"""Staff API endpoints."""

from __future__ import annotations

from typing import Any

from api.client import api_request


def list_staff(
    *,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    role: str | None = None,
    shift: str | None = None,
) -> dict[str, Any]:
    """Fetch a paginated staff list."""
    return api_request(
        "GET",
        "/staff/",
        params={
            "page": page,
            "limit": limit,
            "search": search,
            "role": role,
            "shift": shift,
        },
        auth=True,
    )


def get_staff(staff_id: int) -> dict[str, Any]:
    """Fetch a single staff member by ID."""
    return api_request("GET", f"/staff/{staff_id}", auth=True)


def create_staff(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a new staff member."""
    return api_request("POST", "/staff/", json=payload, auth=True)


def update_staff(staff_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Update an existing staff member."""
    return api_request("PUT", f"/staff/{staff_id}", json=payload, auth=True)


def delete_staff(staff_id: int) -> dict[str, Any]:
    """Permanently delete a staff member."""
    return api_request("DELETE", f"/staff/{staff_id}", auth=True)
