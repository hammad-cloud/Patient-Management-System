"""Staff CRUD API endpoints (JWT protected)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.crud import staff as staff_crud
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.staff import (
    PaginatedStaffList,
    StaffCreate,
    StaffListItem,
    StaffRead,
    StaffShift,
    StaffUpdate,
)

router = APIRouter(prefix="/staff", tags=["staff"])


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a staff member",
)
def create_staff(
    staff_in: StaffCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Create a new staff record. Requires admin JWT."""
    if staff_crud.get_staff_by_phone(db, phone=staff_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A staff member with this phone number already exists.",
        )

    if staff_crud.get_staff_by_email(db, email=staff_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A staff member with this email already exists.",
        )

    staff_crud.create_staff(db, staff_in=staff_in)
    return MessageResponse(message="Staff created successfully.")


@router.get(
    "/",
    response_model=PaginatedStaffList,
    summary="List staff",
)
def list_staff(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(
        default=None,
        max_length=100,
        description="Search by name, role, email, or phone",
    ),
    role: str | None = Query(
        default=None,
        max_length=100,
        description="Filter by role",
    ),
    shift: StaffShift | None = Query(
        default=None,
        description="Filter by shift: morning, evening, or night",
    ),
) -> PaginatedStaffList:
    """Return a paginated staff list. Requires admin JWT."""
    total = staff_crud.count_staff(
        db,
        search=search,
        role=role,
        shift=shift,
    )
    total_pages = max(1, (total + limit - 1) // limit) if total else 0
    skip = (page - 1) * limit
    staff_members = staff_crud.get_staff_list(
        db,
        skip=skip,
        limit=limit,
        search=search,
        role=role,
        shift=shift,
    )

    return PaginatedStaffList(
        items=[StaffListItem.model_validate(member) for member in staff_members],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get(
    "/{staff_id}",
    response_model=StaffRead,
    summary="Get a staff member by ID",
)
def get_staff(
    staff_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> StaffRead:
    """Return a single staff member by ID. Requires admin JWT."""
    staff = staff_crud.get_staff(db, staff_id=staff_id)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff with id {staff_id} was not found.",
        )
    return staff


@router.put(
    "/{staff_id}",
    response_model=MessageResponse,
    summary="Update a staff member",
)
def update_staff(
    staff_id: int,
    staff_in: StaffUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Update an existing staff member. Requires admin JWT."""
    staff = staff_crud.get_staff(db, staff_id=staff_id)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff with id {staff_id} was not found.",
        )

    if staff_in.phone is not None:
        existing = staff_crud.get_staff_by_phone(db, phone=staff_in.phone)
        if existing is not None and existing.id != staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A staff member with this phone number already exists.",
            )

    if staff_in.email is not None:
        existing = staff_crud.get_staff_by_email(db, email=staff_in.email)
        if existing is not None and existing.id != staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A staff member with this email already exists.",
            )

    staff_crud.update_staff(db, staff=staff, staff_in=staff_in)
    return MessageResponse(message="Staff updated successfully.")


@router.delete(
    "/{staff_id}",
    response_model=MessageResponse,
    summary="Delete a staff member",
)
def delete_staff(
    staff_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> MessageResponse:
    """Delete a staff member by ID. Requires admin JWT."""
    staff = staff_crud.get_staff(db, staff_id=staff_id)
    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff with id {staff_id} was not found.",
        )

    staff_crud.delete_staff(db, staff=staff)
    return MessageResponse(message="Staff deleted successfully.")
