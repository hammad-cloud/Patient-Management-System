"""Doctor CRUD API endpoints (JWT protected)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db, get_read_db
from app.core.cache import cache_delete, cache_get, cache_set
from app.crud import doctor as doctor_crud
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.doctor import (
    DoctorCreate,
    DoctorListItem,
    DoctorRead,
    DoctorUpdate,
    PaginatedDoctorList,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a doctor",
)
def create_doctor(
    doctor_in: DoctorCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Create a new doctor record. Requires admin JWT."""
    if doctor_crud.get_doctor_by_phone(db, phone=doctor_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A doctor with this phone number already exists.",
        )

    if doctor_crud.get_doctor_by_email(db, email=doctor_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A doctor with this email already exists.",
        )

    doctor_crud.create_doctor(db, doctor_in=doctor_in)
    return MessageResponse(message="Doctor created successfully.")


@router.get(
    "/",
    response_model=PaginatedDoctorList,
    summary="List doctors",
)
def list_doctors(
    db: Annotated[Session, Depends(get_read_db)],
    _: Annotated[User, Depends(get_current_admin)],
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(
        default=None,
        max_length=100,
        description="Search by name, email, or specialization",
    ),
    specialization: str | None = Query(
        default=None,
        max_length=100,
        description="Filter by specialization",
    ),
) -> PaginatedDoctorList:
    """Return a paginated doctor list. Requires admin JWT."""
    total = doctor_crud.count_doctors(
        db,
        search=search,
        specialization=specialization,
    )
    total_pages = max(1, (total + limit - 1) // limit) if total else 0
    skip = (page - 1) * limit
    doctors = doctor_crud.get_doctors(
        db,
        skip=skip,
        limit=limit,
        search=search,
        specialization=specialization,
    )

    return PaginatedDoctorList(
        items=[DoctorListItem.model_validate(doctor) for doctor in doctors],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get(
    "/{doctor_id}",
    response_model=DoctorRead,
    summary="Get a doctor by ID",
)
def get_doctor(
    doctor_id: int,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> DoctorRead:
    """Return a single doctor by ID (Redis cached). Requires admin JWT."""
    cache_key = f"doctor:{doctor_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return DoctorRead.model_validate(cached)

    doctor = doctor_crud.get_doctor(db, doctor_id=doctor_id)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} was not found.",
        )
    doctor_read = DoctorRead.model_validate(doctor)
    cache_set(cache_key, doctor_read.model_dump(mode="json"))
    response.headers["X-Cache"] = "MISS"
    return doctor_read


@router.put(
    "/{doctor_id}",
    response_model=MessageResponse,
    summary="Update a doctor",
)
def update_doctor(
    doctor_id: int,
    doctor_in: DoctorUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Update an existing doctor. Requires admin JWT."""
    doctor = doctor_crud.get_doctor(db, doctor_id=doctor_id)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} was not found.",
        )

    if doctor_in.phone is not None:
        existing = doctor_crud.get_doctor_by_phone(db, phone=doctor_in.phone)
        if existing is not None and existing.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A doctor with this phone number already exists.",
            )

    if doctor_in.email is not None:
        existing = doctor_crud.get_doctor_by_email(db, email=doctor_in.email)
        if existing is not None and existing.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A doctor with this email already exists.",
            )

    doctor_crud.update_doctor(db, doctor=doctor, doctor_in=doctor_in)
    cache_delete(f"doctor:{doctor_id}")
    return MessageResponse(message="Doctor updated successfully.")


@router.delete(
    "/{doctor_id}",
    response_model=MessageResponse,
    summary="Delete a doctor",
)
def delete_doctor(
    doctor_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Delete a doctor by ID. Requires admin JWT."""
    from app.crud import patient as patient_crud

    doctor = doctor_crud.get_doctor(db, doctor_id=doctor_id)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} was not found.",
        )

    assigned = patient_crud.count_patients_for_doctor(db, doctor_id=doctor_id)
    if assigned > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot delete doctor with id {doctor_id} because "
                f"{assigned} patient(s) are still assigned."
            ),
        )

    doctor_crud.delete_doctor(db, doctor=doctor)
    cache_delete(f"doctor:{doctor_id}")
    return MessageResponse(message="Doctor deleted successfully.")
