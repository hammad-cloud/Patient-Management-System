"""Staff create / edit form component."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.validators import validate_staff_form

SHIFT_OPTIONS = ["morning", "evening", "night"]


def _default_form_values(staff: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build default values for create or edit mode."""
    if not staff:
        return {
            "full_name": "",
            "role": "",
            "shift": "morning",
            "email": "",
            "phone": "",
            "salary": "45000.00",
        }

    salary = staff.get("salary")
    shift = str(staff.get("shift") or "morning").lower()
    if shift not in SHIFT_OPTIONS:
        shift = "morning"

    return {
        "full_name": staff.get("full_name") or "",
        "role": staff.get("role") or "",
        "shift": shift,
        "email": staff.get("email") or "",
        "phone": staff.get("phone") or "",
        "salary": f"{float(salary):.2f}" if salary is not None else "0.00",
    }


def render_staff_form(
    *,
    mode: str,
    staff: dict[str, Any] | None = None,
    form_key: str,
) -> dict[str, Any] | None:
    """
    Render staff form and return a validated payload on submit.

    Returns:
        Payload dict when the form is submitted and valid, otherwise None.
    """
    defaults = _default_form_values(staff)

    with st.form(form_key, clear_on_submit=False, border=False):
        st.markdown(
            f"<p class='panel-label'>{'Edit staff' if mode == 'edit' else 'New staff'}</p>",
            unsafe_allow_html=True,
        )

        full_name = st.text_input("Full name *", value=defaults["full_name"])
        col1, col2 = st.columns(2)
        with col1:
            role = st.text_input(
                "Role *",
                value=defaults["role"],
                placeholder="e.g. Nurse, Receptionist",
            )
            email = st.text_input("Email *", value=defaults["email"])
            shift = st.selectbox(
                "Shift *",
                options=SHIFT_OPTIONS,
                index=SHIFT_OPTIONS.index(defaults["shift"]),
                format_func=lambda v: v.capitalize(),
            )
        with col2:
            phone = st.text_input("Phone *", value=defaults["phone"])
            salary = st.text_input(
                "Salary *",
                value=defaults["salary"],
                placeholder="45000.00",
            )

        submitted = st.form_submit_button(
            "Save staff" if mode == "edit" else "Create staff",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None

    errors, payload = validate_staff_form(
        {
            "full_name": full_name,
            "role": role,
            "shift": shift,
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
