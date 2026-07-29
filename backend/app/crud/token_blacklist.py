"""Helpers for revoking and checking JWT access tokens."""

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.token_blacklist import TokenBlacklist


def is_token_revoked(db: Session, jti: str) -> bool:
    """Return True if the token ID has been revoked."""
    statement = select(TokenBlacklist.id).where(TokenBlacklist.jti == jti)
    return db.execute(statement).scalar_one_or_none() is not None


def revoke_token(db: Session, *, jti: str, expires_at: datetime) -> TokenBlacklist:
    """Add a token ID to the blacklist."""
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    existing = db.execute(
        select(TokenBlacklist).where(TokenBlacklist.jti == jti)
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    entry = TokenBlacklist(jti=jti, expires_at=expires_at)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def cleanup_expired_tokens(db: Session) -> int:
    """Remove expired blacklist rows and return how many were deleted."""
    result = db.execute(
        delete(TokenBlacklist).where(TokenBlacklist.expires_at <= datetime.now(UTC))
    )
    db.commit()
    return int(result.rowcount or 0)
