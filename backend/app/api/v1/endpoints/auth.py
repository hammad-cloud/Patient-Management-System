"""Authentication endpoints (login + logout, no public signup)."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_token_payload, get_db, get_token_expiry
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.crud import token_blacklist as token_blacklist_crud
from app.crud import user as user_crud
from app.schemas.auth import LoginRequest, Token
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post(
    "/login",
    response_model=Token,
    summary="Admin login",
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate an admin and return a JWT access token."""
    user = user_crud.get_user_by_email(db, email=credentials.email)
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Admin logout",
)
def logout(
    payload: Annotated[dict, Depends(get_current_token_payload)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """Revoke the current access token so it can no longer be used."""
    jti = str(payload["jti"])
    expires_at = get_token_expiry(payload)

    token_blacklist_crud.revoke_token(db, jti=jti, expires_at=expires_at)
    token_blacklist_crud.cleanup_expired_tokens(db)

    return MessageResponse(message="Signed out successfully.")
