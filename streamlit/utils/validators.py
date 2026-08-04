"""Client-side validation helpers mirroring backend rules."""

from __future__ import annotations

import re
from typing import Any

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_login(email: str, password: str) -> list[str]:
    """Validate login form fields. Returns a list of error messages."""
    errors: list[str] = []
    email = (email or "").strip()
    password = password or ""

    if not email:
        errors.append("Email is required.")
    elif not EMAIL_PATTERN.match(email):
        errors.append("Enter a valid email address.")

    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters.")

    return errors


def _parse_diseases(raw: str) -> list[str]:
    """Split comma-separated diseases, trim, and dedupe (case-insensitive)."""
    seen: set[str] = set()
    diseases: list[str] = []
    for part in (raw or "").split(","):
        name = part.strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        diseases.append(name)
    return diseases


def validate_patient_form(raw: dict[str, Any]) -> tuple[list[str], dict[str, Any] | None]:
    """
    Validate patient form input and build an API payload.

    Returns:
        (errors, payload) — payload is None when validation fails.
    """
    errors: list[str] = []

    full_name = str(raw.get("full_name") or "").strip()
    phone = str(raw.get("phone") or "").strip()
    email_raw = str(raw.get("email") or "").strip()
    address_raw = str(raw.get("address") or "").strip()
    medical_history_raw = str(raw.get("medical_history") or "").strip()
    gender = str(raw.get("gender") or "").strip()
    status = str(raw.get("status") or "").strip()
    diseases = _parse_diseases(str(raw.get("diseases_text") or ""))

    try:
        age = int(raw.get("age"))
    except (TypeError, ValueError):
        age = -1

    try:
        doctor_id = int(raw.get("doctor_id"))
    except (TypeError, ValueError):
        doctor_id = 0

    if not full_name:
        errors.append("Full name is required.")
    elif not (2 <= len(full_name) <= 150):
        errors.append("Full name must be between 2 and 150 characters.")

    if age < 0 or age > 150:
        errors.append("Age must be a number between 0 and 150.")

    if gender not in {"male", "female", "other"}:
        errors.append("Gender is required.")

    if status not in {"active", "inactive"}:
        errors.append("Status is required.")

    if not phone:
        errors.append("Phone is required.")
    elif not (7 <= len(phone) <= 20):
        errors.append("Phone must be between 7 and 20 characters.")

    if email_raw and not EMAIL_PATTERN.match(email_raw):
        errors.append("Enter a valid email address.")

    if address_raw and len(address_raw) > 255:
        errors.append("Address must be at most 255 characters.")

    if not diseases:
        errors.append("Add at least one disease.")

    if doctor_id <= 0:
        errors.append("Assigned doctor is required.")

    if errors:
        return errors, None

    payload: dict[str, Any] = {
        "full_name": full_name,
        "age": age,
        "gender": gender,
        "status": status,
        "phone": phone,
        "email": email_raw or None,
        "address": address_raw or None,
        "diseases": diseases,
        "medical_history": medical_history_raw or None,
        "doctor_id": doctor_id,
    }
    return [], payload


def validate_doctor_form(raw: dict[str, Any]) -> tuple[list[str], dict[str, Any] | None]:
    """
    Validate doctor form input and build an API payload.

    Returns:
        (errors, payload) — payload is None when validation fails.
    """
    errors: list[str] = []

    full_name = str(raw.get("full_name") or "").strip()
    specialization = str(raw.get("specialization") or "").strip()
    email = str(raw.get("email") or "").strip()
    phone = str(raw.get("phone") or "").strip()
    salary_raw = str(raw.get("salary") or "").strip()

    if not full_name:
        errors.append("Full name is required.")
    elif not (2 <= len(full_name) <= 150):
        errors.append("Full name must be between 2 and 150 characters.")

    if not specialization:
        errors.append("Specialization is required.")
    elif not (2 <= len(specialization) <= 100):
        errors.append("Specialization must be between 2 and 100 characters.")

    if not email:
        errors.append("Email is required.")
    elif not EMAIL_PATTERN.match(email):
        errors.append("Enter a valid email address.")

    if not phone:
        errors.append("Phone is required.")
    elif not (7 <= len(phone) <= 20):
        errors.append("Phone must be between 7 and 20 characters.")

    salary: float | None = None
    try:
        salary = float(salary_raw)
        if salary <= 0:
            errors.append("Salary must be greater than 0.")
    except ValueError:
        errors.append("Salary must be a valid number.")

    if errors:
        return errors, None

    payload: dict[str, Any] = {
        "full_name": full_name,
        "specialization": specialization,
        "email": email,
        "phone": phone,
        "salary": f"{salary:.2f}",
    }
    return [], payload


def validate_staff_form(raw: dict[str, Any]) -> tuple[list[str], dict[str, Any] | None]:
    """
    Validate staff form input and build an API payload.

    Returns:
        (errors, payload) — payload is None when validation fails.
    """
    errors: list[str] = []

    full_name = str(raw.get("full_name") or "").strip()
    role = str(raw.get("role") or "").strip()
    shift = str(raw.get("shift") or "").strip().lower()
    email = str(raw.get("email") or "").strip()
    phone = str(raw.get("phone") or "").strip()
    salary_raw = str(raw.get("salary") or "").strip()

    if not full_name:
        errors.append("Full name is required.")
    elif not (2 <= len(full_name) <= 150):
        errors.append("Full name must be between 2 and 150 characters.")

    if not role:
        errors.append("Role is required.")
    elif not (2 <= len(role) <= 100):
        errors.append("Role must be between 2 and 100 characters.")

    if shift not in {"morning", "evening", "night"}:
        errors.append("Shift must be morning, evening, or night.")

    if not email:
        errors.append("Email is required.")
    elif not EMAIL_PATTERN.match(email):
        errors.append("Enter a valid email address.")

    if not phone:
        errors.append("Phone is required.")
    elif not (7 <= len(phone) <= 20):
        errors.append("Phone must be between 7 and 20 characters.")

    salary: float | None = None
    try:
        salary = float(salary_raw)
        if salary <= 0:
            errors.append("Salary must be greater than 0.")
    except ValueError:
        errors.append("Salary must be a valid number.")

    if errors:
        return errors, None

    payload: dict[str, Any] = {
        "full_name": full_name,
        "role": role,
        "shift": shift,
        "email": email,
        "phone": phone,
        "salary": f"{salary:.2f}",
    }
    return [], payload
