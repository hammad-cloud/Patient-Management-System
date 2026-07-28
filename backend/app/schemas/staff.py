"""Staff create, update, and response schemas."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StaffShift(str, Enum):
    """Allowed shift values for hospital staff."""

    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"


class StaffBase(BaseModel):
    """Shared staff fields used across create and response schemas."""

    full_name: str = Field(..., min_length=2, max_length=150, examples=["Fatima Noor"])
    role: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Nurse"],
    )
    shift: StaffShift = Field(..., examples=[StaffShift.MORNING])
    email: EmailStr = Field(..., examples=["fatima.noor@hospital.com"])
    phone: str = Field(..., min_length=7, max_length=20, examples=["03005556677"])
    salary: Decimal = Field(
        ...,
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["45000.00"],
    )

    @field_validator("full_name", "role")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty.")
        return cleaned

    @field_validator("phone")
    @classmethod
    def strip_phone(cls, value: str) -> str:
        return value.strip()


class StaffCreate(StaffBase):
    """Payload required to create a new staff member."""

    pass


class StaffUpdate(BaseModel):
    """Payload for staff updates. All fields are optional."""

    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    role: str | None = Field(default=None, min_length=2, max_length=100)
    shift: StaffShift | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    salary: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)

    @field_validator("full_name", "role")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty.")
        return cleaned

    @field_validator("phone")
    @classmethod
    def strip_optional_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class StaffRead(StaffBase):
    """Full staff data returned by detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class StaffListItem(BaseModel):
    """Lean staff fields returned by the paginated list endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    role: str
    shift: StaffShift
    email: EmailStr
    phone: str
    salary: Decimal


class PaginatedStaffList(BaseModel):
    """Paginated staff list response."""

    items: list[StaffListItem]
    total: int
    page: int
    limit: int
    total_pages: int
