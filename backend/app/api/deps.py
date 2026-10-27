"""Shared API dependencies (database session and JWT auth)."""

from collections.abc import Generator
from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.crud import token_blacklist as token_blacklist_crud
from app.crud import user as user_crud
from app.db.session import get_db as _get_db
from app.db.session import get_read_db as _get_read_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session per request."""
    yield from _get_db()


def get_read_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a read-replica session per request."""
    yield from _get_read_db()


def get_current_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Validate the Bearer JWT and ensure it has not been revoked."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        jti = payload.get("jti")
        exp = payload.get("exp")
        if subject is None or jti is None or exp is None:
            raise credentials_exception
    except (jwt.PyJWTError, ValueError, TypeError) as exc:
        raise credentials_exception from exc

    if token_blacklist_crud.is_token_revoked(db, jti=str(jti)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload["raw_token"] = token
    return payload


def get_current_user(
    payload: Annotated[dict, Depends(get_current_token_payload)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Return the authenticated user for the current request."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = user_crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )
    return user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the current user has the admin role."""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user


def get_token_expiry(payload: dict) -> datetime:
    """Convert a JWT exp claim into an aware UTC datetime."""
    exp = payload["exp"]
    if isinstance(exp, datetime):
        return exp if exp.tzinfo else exp.replace(tzinfo=UTC)
    return datetime.fromtimestamp(exp, tz=UTC)
