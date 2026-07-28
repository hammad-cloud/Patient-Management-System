"""Shared API response schemas."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Simple success message returned by mutating endpoints."""

    message: str
