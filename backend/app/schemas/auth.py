"""Auth request and response schemas."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials required to log in."""

    email: EmailStr = Field(..., examples=["admin123@gmail.com"])
    password: str = Field(..., min_length=8, examples=["12345678"])


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"
