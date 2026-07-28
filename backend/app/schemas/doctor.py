"""Doctor create, update, and response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class DoctorBase(BaseModel):
    """Shared doctor fields used across create and response schemas."""

    full_name: str = Field(..., min_length=2, max_length=150, examples=["Dr. Ahmed Khan"])
    specialization: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Cardiology"],
    )
    email: EmailStr = Field(..., examples=["ahmed.khan@hospital.com"])
    phone: str = Field(..., min_length=7, max_length=20, examples=["03001112233"])
    salary: Decimal = Field(
        ...,
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["150000.00"],
    )

    @field_validator("full_name", "specialization")
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


class DoctorCreate(DoctorBase):
    """Payload required to create a new doctor."""

    pass


class DoctorUpdate(BaseModel):
    """Payload for doctor updates. All fields are optional."""

    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    specialization: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    salary: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)

    @field_validator("full_name", "specialization")
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


class DoctorRead(DoctorBase):
    """Full doctor data returned by detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DoctorListItem(BaseModel):
    """Lean doctor fields returned by the paginated list endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    specialization: str
    email: EmailStr
    phone: str
    salary: Decimal


class PaginatedDoctorList(BaseModel):
    """Paginated doctor list response."""

    items: list[DoctorListItem]
    total: int
    page: int
    limit: int
    total_pages: int
