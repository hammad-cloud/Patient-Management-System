"""Doctor create / edit form component."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.validators import validate_doctor_form


def _default_form_values(doctor: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build default values for create or edit mode."""
    if not doctor:
        return {
            "full_name": "",
            "specialization": "",
            "email": "",
            "phone": "",
            "salary": "100000.00",
        }

    salary = doctor.get("salary")
    return {
        "full_name": doctor.get("full_name") or "",
        "specialization": doctor.get("specialization") or "",
        "email": doctor.get("email") or "",
        "phone": doctor.get("phone") or "",
        "salary": f"{float(salary):.2f}" if salary is not None else "0.00",
    }


def render_doctor_form(
    *,
    mode: str,
    doctor: dict[str, Any] | None = None,
    form_key: str,
) -> dict[str, Any] | None:
    """
    Render doctor form and return a validated payload on submit.

    Returns:
        Payload dict when the form is submitted and valid, otherwise None.
    """
    defaults = _default_form_values(doctor)

    with st.form(form_key, clear_on_submit=False, border=False):
        st.markdown(
            f"<p class='panel-label'>{'Edit doctor' if mode == 'edit' else 'New doctor'}</p>",
            unsafe_allow_html=True,
        )

        full_name = st.text_input("Full name *", value=defaults["full_name"])
        col1, col2 = st.columns(2)
        with col1:
            specialization = st.text_input(
                "Specialization *",
                value=defaults["specialization"],
                placeholder="e.g. Cardiology",
            )
            email = st.text_input("Email *", value=defaults["email"])
        with col2:
            phone = st.text_input("Phone *", value=defaults["phone"])
            salary = st.text_input(
                "Salary *",
                value=defaults["salary"],
                placeholder="150000.00",
            )

        submitted = st.form_submit_button(
            "Save doctor" if mode == "edit" else "Create doctor",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None

    errors, payload = validate_doctor_form(
        {
            "full_name": full_name,
            "specialization": specialization,
            "email": email,
            "phone": phone,
            "salary": salary,
        }
    )
    if errors:
        for error in errors:
            st.error(error)
        return None

    return payload
