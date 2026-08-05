"""Patient create / edit form component."""

from __future__ import annotations

from typing import Any

import streamlit as st

from api import doctors as doctors_api
from api.client import ApiError
from utils.validators import validate_patient_form


def _load_doctor_options() -> list[dict[str, Any]]:
    """Fetch doctors for the assignment dropdown."""
    try:
        data = doctors_api.list_doctors(page=1, limit=100)
        return list(data.get("items") or [])
    except ApiError as exc:
        st.error(f"Could not load doctors: {exc.detail}")
        return []


def _default_form_values(patient: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build default values for create or edit mode."""
    if not patient:
        return {
            "full_name": "",
            "age": 25,
            "gender": "male",
            "status": "active",
            "phone": "",
            "email": "",
            "address": "",
            "diseases_text": "",
            "medical_history": "",
            "doctor_id": None,
        }

    diseases = patient.get("diseases") or []
    return {
        "full_name": patient.get("full_name") or "",
        "age": int(patient.get("age") or 0),
        "gender": patient.get("gender") or "male",
        "status": patient.get("status") or "active",
        "phone": patient.get("phone") or "",
        "email": patient.get("email") or "",
        "address": patient.get("address") or "",
        "diseases_text": ", ".join(diseases),
        "medical_history": patient.get("medical_history") or "",
        "doctor_id": patient.get("doctor_id"),
    }


def render_patient_form(
    *,
    mode: str,
    patient: dict[str, Any] | None = None,
    form_key: str,
) -> dict[str, Any] | None:
    """
    Render patient form and return a validated payload on submit.

    Returns:
        Payload dict when the form is submitted and valid, otherwise None.
    """
    defaults = _default_form_values(patient)
    doctors = _load_doctor_options()
    doctor_ids = [int(item["id"]) for item in doctors]

    if not doctor_ids:
        st.warning("Add at least one doctor before creating or assigning patients.")
        return None

    default_doctor_id = defaults["doctor_id"]
    if default_doctor_id not in doctor_ids:
        default_doctor_id = doctor_ids[0]

    with st.form(form_key, clear_on_submit=False, border=False):
        st.markdown(
            f"<p class='panel-label'>{'Edit patient' if mode == 'edit' else 'New patient'}</p>",
            unsafe_allow_html=True,
        )

        full_name = st.text_input("Full name *", value=defaults["full_name"])
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(
                "Age *",
                min_value=0,
                max_value=150,
                value=int(defaults["age"]),
                step=1,
            )
            gender = st.selectbox(
                "Gender *",
                options=["male", "female", "other"],
                index=["male", "female", "other"].index(defaults["gender"]),
            )
            doctor_id = st.selectbox(
                "Assigned doctor *",
                options=doctor_ids,
                index=doctor_ids.index(int(default_doctor_id)),
                format_func=lambda did: next(
                    (
                        f"{item['full_name']} — {item['specialization']} (#{item['id']})"
                        for item in doctors
                        if int(item["id"]) == did
                    ),
                    str(did),
                ),
            )
        with col2:
            status = st.selectbox(
                "Status *",
                options=["active", "inactive"],
                index=["active", "inactive"].index(defaults["status"]),
            )
            phone = st.text_input("Phone *", value=defaults["phone"])

        email = st.text_input("Email", value=defaults["email"])
        address = st.text_input("Address", value=defaults["address"])
        diseases_text = st.text_input(
            "Diseases * (comma-separated)",
            value=defaults["diseases_text"],
            help="Example: Diabetes, Hypertension",
        )
        medical_history = st.text_area(
            "Medical history",
            value=defaults["medical_history"],
            height=100,
        )

        submitted = st.form_submit_button(
            "Save patient" if mode == "edit" else "Create patient",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None

    raw = {
        "full_name": full_name,
        "age": age,
        "gender": gender,
        "status": status,
        "phone": phone,
        "email": email,
        "address": address,
        "diseases_text": diseases_text,
        "medical_history": medical_history,
        "doctor_id": doctor_id,
    }
    errors, payload = validate_patient_form(raw)
    if errors:
        for error in errors:
            st.error(error)
        return None

    return payload
