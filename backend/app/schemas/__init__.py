"""Pydantic schemas for request and response validation."""

from app.schemas.auth import LoginRequest, Token
from app.schemas.doctor import (
    DoctorCreate,
    DoctorListItem,
    DoctorRead,
    DoctorUpdate,
    PaginatedDoctorList,
)
from app.schemas.patient import (
    Gender,
    PaginatedPatientList,
    PatientCreate,
    PatientListItem,
    PatientRead,
    PatientUpdate,
)
from app.schemas.staff import (
    PaginatedStaffList,
    StaffCreate,
    StaffListItem,
    StaffRead,
    StaffShift,
    StaffUpdate,
)
from app.schemas.user import UserRead

__all__ = [
    "DoctorCreate",
    "DoctorListItem",
    "DoctorRead",
    "DoctorUpdate",
    "Gender",
    "LoginRequest",
    "PaginatedDoctorList",
    "PaginatedPatientList",
    "PaginatedStaffList",
    "PatientCreate",
    "PatientListItem",
    "PatientRead",
    "PatientUpdate",
    "StaffCreate",
    "StaffListItem",
    "StaffRead",
    "StaffShift",
    "StaffUpdate",
    "Token",
    "UserRead",
]
