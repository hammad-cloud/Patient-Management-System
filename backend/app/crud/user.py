"""Create, read, and seed helpers for users."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import User, UserRole


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return a user by email, or None if not found."""
    statement = select(User).where(User.email == email)
    return db.execute(statement).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Return a user by ID, or None if not found."""
    return db.get(User, user_id)


def create_admin_user(db: Session, *, email: str, password: str, full_name: str = "Admin") -> User:
    """Create an admin user with a hashed password."""
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ensure_admin_user(db: Session) -> User:
    """Create the default admin account if it does not already exist."""
    settings = get_settings()
    existing = get_user_by_email(db, email=settings.admin_email)
    if existing is not None:
        return existing

    return create_admin_user(
        db,
        email=settings.admin_email,
        password=settings.admin_password,
        full_name="System Admin",
    )
