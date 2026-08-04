"""Shared HTTP client for FastAPI requests."""

from __future__ import annotations

from typing import Any

import httpx
import streamlit as st

from config.settings import get_settings


class ApiError(Exception):
    """Raised when the backend returns an error response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _parse_detail(payload: Any) -> str:
    """Normalize FastAPI error payloads into a readable string."""
    if payload is None:
        return "Unexpected server error."
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        detail = payload.get("detail", payload)
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list):
            messages: list[str] = []
            for item in detail:
                if isinstance(item, dict) and "msg" in item:
                    messages.append(str(item["msg"]))
                else:
                    messages.append(str(item))
            return "; ".join(messages) if messages else "Validation error."
        return str(detail)
    return str(payload)


def api_request(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    auth: bool = False,
) -> Any:
    """
    Send an HTTP request to the FastAPI backend.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE).
        path: Path relative to API base URL (e.g. "/patients/").
        json: Optional JSON body.
        params: Optional query parameters.
        auth: When True, attach Bearer token from session state.
    """
    settings = get_settings()
    headers: dict[str, str] = {"Content-Type": "application/json"}

    if auth:
        token = st.session_state.get("access_token")
        if not token:
            raise ApiError(401, "Authentication required.")
        headers["Authorization"] = f"Bearer {token}"

    # Drop empty query params so the backend receives clean filters.
    clean_params: dict[str, Any] | None = None
    if params:
        clean_params = {k: v for k, v in params.items() if v not in (None, "")}

    url = f"{settings.api_base_url.rstrip('/')}{path}"

    try:
        with httpx.Client(timeout=settings.request_timeout_seconds) as client:
            response = client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=json,
                params=clean_params,
            )
    except httpx.RequestError as exc:
        raise ApiError(0, f"Cannot reach API at {settings.api_base_url}. ({exc})") from exc

    if response.status_code == 204:
        return None

    try:
        payload = response.json() if response.content else None
    except ValueError:
        payload = None

    if response.is_error:
        raise ApiError(response.status_code, _parse_detail(payload))

    return payload
