"""Patient CRUD API endpoints (JWT protected)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.crud import doctor as doctor_crud
from app.crud import patient as patient_crud
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.patient import (
    Gender,
    PaginatedPatientList,
    PatientCounts,
    PatientCreate,
    PatientListItem,
    PatientRead,
    PatientStatus,
    PatientUpdate,
)

router = APIRouter(prefix="/patients", tags=["patients"])


def _ensure_doctor_exists(db: Session, doctor_id: int) -> None:
    """Raise 400 when the assigned doctor does not exist."""
    if doctor_crud.get_doctor(db, doctor_id=doctor_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor with id {doctor_id} was not found.",
        )


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a patient",
)
def create_patient(
    patient_in: PatientCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Create a new patient record linked to a doctor. Requires admin JWT."""
    _ensure_doctor_exists(db, patient_in.doctor_id)

    if patient_crud.get_patient_by_phone(db, phone=patient_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A patient with this phone number already exists.",
        )

    if patient_in.email and patient_crud.get_patient_by_email(db, email=patient_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A patient with this email already exists.",
        )

    patient_crud.create_patient(db, patient_in=patient_in)
    return MessageResponse(message="Patient created successfully.")


@router.get(
    "/",
    response_model=PaginatedPatientList,
    summary="List patients",
)
def list_patients(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(
        default=None,
        max_length=100,
        description="Search by name, email, or disease",
    ),
    gender: Gender | None = Query(
        default=None,
        description="Filter by gender: male, female, or other",
    ),
    status: PatientStatus | None = Query(
        default=None,
        description="Filter by status: active or inactive",
    ),
    doctor_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter by assigned doctor ID",
    ),
) -> PaginatedPatientList:
    """Return a lean, paginated patient list. Requires admin JWT."""
    total = patient_crud.count_patients(
        db,
        search=search,
        gender=gender,
        status=status,
        doctor_id=doctor_id,
    )
    all_count, active_count = patient_crud.get_patient_counts(db)
    total_pages = max(1, (total + limit - 1) // limit) if total else 0
    skip = (page - 1) * limit
    patients = patient_crud.get_patients(
        db,
        skip=skip,
        limit=limit,
        search=search,
        gender=gender,
        status=status,
        doctor_id=doctor_id,
    )

    return PaginatedPatientList(
        items=[PatientListItem.model_validate(patient) for patient in patients],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        counts=PatientCounts(all=all_count, active=active_count),
    )


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
    summary="Get a patient by ID",
)
def get_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> PatientRead:
    """Return a single patient by ID. Requires admin JWT."""
    patient = patient_crud.get_patient(db, patient_id=patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} was not found.",
        )
    return patient


@router.patch(
    "/{patient_id}",
    response_model=MessageResponse,
    summary="Update a patient",
)
def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Partially update an existing patient. Requires admin JWT."""
    patient = patient_crud.get_patient(db, patient_id=patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} was not found.",
        )

    if patient_in.doctor_id is not None:
        _ensure_doctor_exists(db, patient_in.doctor_id)

    if patient_in.phone is not None:
        existing = patient_crud.get_patient_by_phone(db, phone=patient_in.phone)
        if existing is not None and existing.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this phone number already exists.",
            )

    if patient_in.email is not None:
        existing = patient_crud.get_patient_by_email(db, email=patient_in.email)
        if existing is not None and existing.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this email already exists.",
            )

    patient_crud.update_patient(db, patient=patient, patient_in=patient_in)
    return MessageResponse(message="Patient updated successfully.")


@router.delete(
    "/{patient_id}",
    response_model=MessageResponse,
    summary="Delete a patient",
)
def delete_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Delete a patient by ID. Requires admin JWT."""
    patient = patient_crud.get_patient(db, patient_id=patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} was not found.",
        )

    patient_crud.delete_patient(db, patient=patient)
    return MessageResponse(message="Patient deleted successfully.")
