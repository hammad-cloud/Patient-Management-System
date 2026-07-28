"""Patient create, update, and response schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Gender(str, Enum):
    """Allowed gender values for a patient."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class PatientStatus(str, Enum):
    """Allowed status values for a patient record."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class AssignedDoctorSummary(BaseModel):
    """Compact doctor info embedded in patient responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    specialization: str


class PatientBase(BaseModel):
    """Shared patient fields used across create and response schemas."""

    full_name: str = Field(..., min_length=2, max_length=150, examples=["Ali Khan"])
    age: int = Field(..., ge=0, le=150, examples=[35])
    gender: Gender = Field(..., examples=[Gender.MALE])
    status: PatientStatus = Field(
        default=PatientStatus.ACTIVE,
        examples=[PatientStatus.ACTIVE],
    )
    phone: str = Field(..., min_length=7, max_length=20, examples=["03001234567"])
    email: EmailStr | None = Field(default=None, examples=["ali@example.com"])
    address: str | None = Field(default=None, max_length=255, examples=["Lahore, Pakistan"])
    diseases: list[str] = Field(
        default_factory=list,
        examples=[["Diabetes", "Hypertension"]],
    )
    medical_history: str | None = Field(
        default=None,
        examples=["Family history of heart disease"],
    )

    @field_validator("diseases")
    @classmethod
    def normalize_diseases(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in value:
            disease = item.strip()
            if not disease:
                continue
            key = disease.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(disease)
        return cleaned


class PatientCreate(PatientBase):
    """Payload required to create a new patient."""

    doctor_id: int = Field(..., gt=0, examples=[1], description="Assigned doctor ID")


class PatientUpdate(BaseModel):
    """Payload for partial patient updates. All fields are optional."""

    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    age: int | None = Field(default=None, ge=0, le=150)
    gender: Gender | None = None
    status: PatientStatus | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=255)
    diseases: list[str] | None = None
    medical_history: str | None = None
    doctor_id: int | None = Field(default=None, gt=0)

    @field_validator("diseases")
    @classmethod
    def normalize_diseases(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in value:
            disease = item.strip()
            if not disease:
                continue
            key = disease.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(disease)
        return cleaned


class PatientRead(PatientBase):
    """Full patient data returned by detail endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int | None = None
    doctor: AssignedDoctorSummary | None = None
    created_at: datetime
    updated_at: datetime


class PatientListItem(BaseModel):
    """Lean patient fields returned by the paginated list endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    age: int
    gender: Gender
    status: PatientStatus
    phone: str
    email: EmailStr | None = None
    diseases: list[str] = Field(default_factory=list)
    doctor_id: int | None = None
    doctor: AssignedDoctorSummary | None = None


class PatientCounts(BaseModel):
    """Overall patient counts, independent of list filters."""

    all: int = Field(..., ge=0, description="Total patients in the system")
    active: int = Field(..., ge=0, description="Patients with active status")


class PaginatedPatientList(BaseModel):
    """Paginated patient list response."""

    items: list[PatientListItem]
    total: int
    page: int
    limit: int
    total_pages: int
    counts: PatientCounts
