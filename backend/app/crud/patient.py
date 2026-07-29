"""Create, read, update, and delete helpers for patients."""

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import ColumnElement

from app.models.patient import Patient
from app.schemas.patient import Gender, PatientCreate, PatientStatus, PatientUpdate


def get_patient(db: Session, patient_id: int) -> Patient | None:
    """Return a single patient by ID (with doctor), or None if not found."""
    statement = (
        select(Patient)
        .options(joinedload(Patient.doctor))
        .where(Patient.id == patient_id)
    )
    return db.execute(statement).unique().scalar_one_or_none()


def get_patient_by_phone(db: Session, phone: str) -> Patient | None:
    """Return a patient by phone number, or None if not found."""
    statement = select(Patient).where(Patient.phone == phone)
    return db.execute(statement).scalar_one_or_none()


def get_patient_by_email(db: Session, email: str) -> Patient | None:
    """Return a patient by email, or None if not found."""
    statement = select(Patient).where(Patient.email == email)
    return db.execute(statement).scalar_one_or_none()


def count_patients_for_doctor(db: Session, doctor_id: int) -> int:
    """Return how many patients are assigned to a doctor."""
    statement = (
        select(func.count()).select_from(Patient).where(Patient.doctor_id == doctor_id)
    )
    return int(db.execute(statement).scalar_one())


def _list_filters(
    *,
    search: str | None = None,
    gender: Gender | None = None,
    status: PatientStatus | None = None,
    doctor_id: int | None = None,
) -> list[ColumnElement[bool]]:
    """Build filters for patient list queries."""
    filters: list[ColumnElement[bool]] = []

    query = (search or "").strip()
    if query:
        pattern = f"%{query}%"
        filters.append(
            or_(
                Patient.full_name.ilike(pattern),
                Patient.email.ilike(pattern),
                cast(Patient.diseases, String).ilike(pattern),
            )
        )

    if gender is not None:
        filters.append(Patient.gender == gender.value)

    if status is not None:
        filters.append(Patient.status == status.value)

    if doctor_id is not None:
        filters.append(Patient.doctor_id == doctor_id)

    return filters


def count_patients(
    db: Session,
    *,
    search: str | None = None,
    gender: Gender | None = None,
    status: PatientStatus | None = None,
    doctor_id: int | None = None,
) -> int:
    """Return the total number of patients matching filters."""
    statement = select(func.count()).select_from(Patient)
    filters = _list_filters(
        search=search,
        gender=gender,
        status=status,
        doctor_id=doctor_id,
    )
    if filters:
        statement = statement.where(*filters)
    return int(db.execute(statement).scalar_one())


def get_patient_counts(db: Session) -> tuple[int, int]:
    """Return overall (all, active) patient counts."""
    all_count = int(db.execute(select(func.count()).select_from(Patient)).scalar_one())
    active_count = int(
        db.execute(
            select(func.count())
            .select_from(Patient)
            .where(Patient.status == PatientStatus.ACTIVE.value)
        ).scalar_one()
    )
    return all_count, active_count


def get_patients(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    gender: Gender | None = None,
    status: PatientStatus | None = None,
    doctor_id: int | None = None,
) -> list[Patient]:
    """Return patients filtered/paginated, newest created first."""
    statement = (
        select(Patient)
        .options(joinedload(Patient.doctor))
        .order_by(Patient.created_at.desc(), Patient.id.desc())
    )
    filters = _list_filters(
        search=search,
        gender=gender,
        status=status,
        doctor_id=doctor_id,
    )
    if filters:
        statement = statement.where(*filters)
    statement = statement.offset(skip).limit(limit)
    return list(db.execute(statement).unique().scalars().all())


def create_patient(db: Session, patient_in: PatientCreate) -> Patient:
    """Create and persist a new patient record."""
    patient = Patient(**patient_in.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient: Patient, patient_in: PatientUpdate) -> Patient:
    """Update an existing patient with only the provided fields."""
    update_data = patient_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(patient, field, value)

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: Patient) -> Patient:
    """Delete a patient record and return the deleted object."""
    db.delete(patient)
    db.commit()
    return patient
