"""Create, read, update, and delete helpers for staff."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement

from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffShift, StaffUpdate


def get_staff(db: Session, staff_id: int) -> Staff | None:
    """Return a single staff member by ID, or None if not found."""
    return db.get(Staff, staff_id)


def get_staff_by_phone(db: Session, phone: str) -> Staff | None:
    """Return a staff member by phone number, or None if not found."""
    statement = select(Staff).where(Staff.phone == phone)
    return db.execute(statement).scalar_one_or_none()


def get_staff_by_email(db: Session, email: str) -> Staff | None:
    """Return a staff member by email, or None if not found."""
    statement = select(Staff).where(Staff.email == email)
    return db.execute(statement).scalar_one_or_none()


def _list_filters(
    *,
    search: str | None = None,
    role: str | None = None,
    shift: StaffShift | None = None,
) -> list[ColumnElement[bool]]:
    """Build filters for staff list queries."""
    filters: list[ColumnElement[bool]] = []

    query = (search or "").strip()
    if query:
        pattern = f"%{query}%"
        filters.append(
            or_(
                Staff.full_name.ilike(pattern),
                Staff.role.ilike(pattern),
                Staff.email.ilike(pattern),
                Staff.phone.ilike(pattern),
            )
        )

    role_query = (role or "").strip()
    if role_query:
        filters.append(Staff.role.ilike(f"%{role_query}%"))

    if shift is not None:
        filters.append(Staff.shift == shift.value)

    return filters


def count_staff(
    db: Session,
    *,
    search: str | None = None,
    role: str | None = None,
    shift: StaffShift | None = None,
) -> int:
    """Return the total number of staff matching filters."""
    statement = select(func.count()).select_from(Staff)
    filters = _list_filters(search=search, role=role, shift=shift)
    if filters:
        statement = statement.where(*filters)
    return int(db.execute(statement).scalar_one())


def get_staff_list(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    role: str | None = None,
    shift: StaffShift | None = None,
) -> list[Staff]:
    """Return staff filtered/paginated, newest created first."""
    statement = select(Staff).order_by(Staff.created_at.desc(), Staff.id.desc())
    filters = _list_filters(search=search, role=role, shift=shift)
    if filters:
        statement = statement.where(*filters)
    statement = statement.offset(skip).limit(limit)
    return list(db.execute(statement).scalars().all())


def create_staff(db: Session, staff_in: StaffCreate) -> Staff:
    """Create and persist a new staff record."""
    payload = staff_in.model_dump()
    payload["shift"] = staff_in.shift.value
    staff = Staff(**payload)
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


def update_staff(db: Session, staff: Staff, staff_in: StaffUpdate) -> Staff:
    """Update an existing staff member with only the provided fields."""
    update_data = staff_in.model_dump(exclude_unset=True)
    if "shift" in update_data and update_data["shift"] is not None:
        update_data["shift"] = (
            update_data["shift"].value
            if isinstance(update_data["shift"], StaffShift)
            else update_data["shift"]
        )

    for field, value in update_data.items():
        setattr(staff, field, value)

    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


def delete_staff(db: Session, staff: Staff) -> Staff:
    """Delete a staff record and return the deleted object."""
    db.delete(staff)
    db.commit()
    return staff
