"""Create, read, update, and delete helpers for doctors."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate


def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
    """Return a single doctor by ID, or None if not found."""
    return db.get(Doctor, doctor_id)


def get_doctor_by_phone(db: Session, phone: str) -> Doctor | None:
    """Return a doctor by phone number, or None if not found."""
    statement = select(Doctor).where(Doctor.phone == phone)
    return db.execute(statement).scalar_one_or_none()


def get_doctor_by_email(db: Session, email: str) -> Doctor | None:
    """Return a doctor by email, or None if not found."""
    statement = select(Doctor).where(Doctor.email == email)
    return db.execute(statement).scalar_one_or_none()


def _list_filters(
    *,
    search: str | None = None,
    specialization: str | None = None,
) -> list[ColumnElement[bool]]:
    """Build filters for doctor list queries."""
    filters: list[ColumnElement[bool]] = []

    query = (search or "").strip()
    if query:
        pattern = f"%{query}%"
        filters.append(
            or_(
                Doctor.full_name.ilike(pattern),
                Doctor.email.ilike(pattern),
                Doctor.specialization.ilike(pattern),
            )
        )

    specialization_query = (specialization or "").strip()
    if specialization_query:
        filters.append(Doctor.specialization.ilike(f"%{specialization_query}%"))

    return filters


def count_doctors(
    db: Session,
    *,
    search: str | None = None,
    specialization: str | None = None,
) -> int:
    """Return the total number of doctors matching filters."""
    statement = select(func.count()).select_from(Doctor)
    filters = _list_filters(search=search, specialization=specialization)
    if filters:
        statement = statement.where(*filters)
    return int(db.execute(statement).scalar_one())


def get_doctors(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    specialization: str | None = None,
) -> list[Doctor]:
    """Return doctors filtered/paginated, newest created first."""
    statement = select(Doctor).order_by(Doctor.created_at.desc(), Doctor.id.desc())
    filters = _list_filters(search=search, specialization=specialization)
    if filters:
        statement = statement.where(*filters)
    statement = statement.offset(skip).limit(limit)
    return list(db.execute(statement).scalars().all())


def create_doctor(db: Session, doctor_in: DoctorCreate) -> Doctor:
    """Create and persist a new doctor record."""
    doctor = Doctor(**doctor_in.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def update_doctor(db: Session, doctor: Doctor, doctor_in: DoctorUpdate) -> Doctor:
    """Update an existing doctor with only the provided fields."""
    update_data = doctor_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(doctor, field, value)

    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def delete_doctor(db: Session, doctor: Doctor) -> Doctor:
    """Delete a doctor record and return the deleted object."""
    db.delete(doctor)
    db.commit()
    return doctor
