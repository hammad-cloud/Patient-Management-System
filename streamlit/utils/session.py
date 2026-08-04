"""Session-state helpers for authentication and UI state."""

from __future__ import annotations

import streamlit as st

PAGE_PATIENTS = "patients"
PAGE_DOCTORS = "doctors"
PAGE_STAFF = "staff"


def init_session_state() -> None:
    """Ensure required session keys exist with safe defaults."""
    defaults: dict[str, object] = {
        "access_token": None,
        "current_page": PAGE_PATIENTS,
        # Patients
        "patients_page": 1,
        "patients_limit": 10,
        "patients_search": "",
        "patients_gender": "",
        "patients_status": "",
        "patients_doctor_id": "",
        "patients_ui_mode": "list",
        "selected_patient_id": None,
        # Doctors
        "doctors_page": 1,
        "doctors_limit": 10,
        "doctors_search": "",
        "doctors_specialization": "",
        "doctors_ui_mode": "list",
        "selected_doctor_id": None,
        # Staff
        "staff_page": 1,
        "staff_limit": 10,
        "staff_search": "",
        "staff_role": "",
        "staff_shift": "",
        "staff_ui_mode": "list",
        "selected_staff_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Migrate older session key if present.
    if "ui_mode" in st.session_state and "patients_ui_mode" not in st.session_state:
        st.session_state.patients_ui_mode = st.session_state.ui_mode


def is_authenticated() -> bool:
    """Return True when a JWT is present in session state."""
    return bool(st.session_state.get("access_token"))


def set_auth_token(token: str) -> None:
    """Persist access token after successful login."""
    st.session_state.access_token = token


def clear_auth() -> None:
    """Clear auth and reset workspace UI state."""
    st.session_state.access_token = None
    st.session_state.current_page = PAGE_PATIENTS
    st.session_state.patients_ui_mode = "list"
    st.session_state.selected_patient_id = None
    st.session_state.doctors_ui_mode = "list"
    st.session_state.selected_doctor_id = None
    st.session_state.staff_ui_mode = "list"
    st.session_state.selected_staff_id = None


def set_current_page(page: str) -> None:
    """Switch workspace page and reset nested modes to list."""
    st.session_state.current_page = page
    if page == PAGE_PATIENTS:
        set_patients_list_mode()
    elif page == PAGE_DOCTORS:
        set_doctors_list_mode()
    elif page == PAGE_STAFF:
        set_staff_list_mode()


def set_patients_list_mode() -> None:
    """Return UI to the patients list."""
    st.session_state.patients_ui_mode = "list"
    st.session_state.selected_patient_id = None


def set_doctors_list_mode() -> None:
    """Return UI to the doctors list."""
    st.session_state.doctors_ui_mode = "list"
    st.session_state.selected_doctor_id = None


def set_staff_list_mode() -> None:
    """Return UI to the staff list."""
    st.session_state.staff_ui_mode = "list"
    st.session_state.selected_staff_id = None


def set_list_mode() -> None:
    """Alias for set_patients_list_mode."""
    set_patients_list_mode()
