"""Patients workspace — list, create, edit, view, delete."""

from __future__ import annotations

import streamlit as st

from api import patients as patients_api
from api.client import ApiError
from components.layout import render_page_header
from components.patient_form import render_patient_form
from components.patient_table import (
    render_patient_detail,
    render_patient_stats,
    render_patients_table,
)
from utils.session import clear_auth, set_patients_list_mode


def _handle_auth_error(exc: ApiError) -> bool:
    """Clear session and return True when the error is an auth failure."""
    if exc.status_code == 401:
        clear_auth()
        st.warning("Session expired. Please sign in again.")
        st.rerun()
        return True
    return False


def _render_filters() -> None:
    """Render search and filter controls inside a panel."""
    from api import doctors as doctors_api

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<p class="panel-label">Search & filters</p>', unsafe_allow_html=True)

    doctor_options: list[tuple[str, str]] = [("", "All doctors")]
    try:
        doctors = doctors_api.list_doctors(page=1, limit=100).get("items") or []
        doctor_options.extend(
            (
                str(item["id"]),
                f"{item['full_name']} — {item['specialization']}",
            )
            for item in doctors
        )
    except ApiError:
        pass

    doctor_ids = [item[0] for item in doctor_options]
    doctor_labels = {item[0]: item[1] for item in doctor_options}

    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1.4, 0.8])
    with col1:
        st.session_state.patients_search = st.text_input(
            "Search",
            value=st.session_state.patients_search,
            placeholder="Name, email, or disease",
            label_visibility="collapsed",
        )
    with col2:
        gender_options = ["", "male", "female", "other"]
        current_gender = st.session_state.patients_gender
        st.session_state.patients_gender = st.selectbox(
            "Gender",
            options=gender_options,
            index=gender_options.index(current_gender) if current_gender in gender_options else 0,
            format_func=lambda v: "All genders" if v == "" else v.capitalize(),
            label_visibility="collapsed",
        )
    with col3:
        status_options = ["", "active", "inactive"]
        current_status = st.session_state.patients_status
        st.session_state.patients_status = st.selectbox(
            "Status",
            options=status_options,
            index=status_options.index(current_status) if current_status in status_options else 0,
            format_func=lambda v: "All statuses" if v == "" else v.capitalize(),
            label_visibility="collapsed",
        )
    with col4:
        current_doctor = str(st.session_state.get("patients_doctor_id") or "")
        st.session_state.patients_doctor_id = st.selectbox(
            "Doctor",
            options=doctor_ids,
            index=doctor_ids.index(current_doctor) if current_doctor in doctor_ids else 0,
            format_func=lambda v: doctor_labels.get(v, "All doctors"),
            label_visibility="collapsed",
        )
    with col5:
        limit_options = [10, 25, 50, 100]
        current_limit = st.session_state.patients_limit
        st.session_state.patients_limit = st.selectbox(
            "Rows",
            options=limit_options,
            index=limit_options.index(current_limit) if current_limit in limit_options else 0,
            format_func=lambda v: f"{v} rows",
            label_visibility="collapsed",
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_list() -> None:
    """Render the patients list with actions."""
    header_left, header_right = st.columns([3.2, 1])
    with header_left:
        render_page_header(
            "Patients",
            subtitle="Search, filter, and manage patient records.",
        )
    with header_right:
        st.write("")
        st.write("")
        if st.button("Add patient", type="primary", use_container_width=True):
            st.session_state.patients_ui_mode = "create"
            st.rerun()

    _render_filters()

    try:
        data = patients_api.list_patients(
            page=st.session_state.patients_page,
            limit=st.session_state.patients_limit,
            search=st.session_state.patients_search or None,
            gender=st.session_state.patients_gender or None,
            status=st.session_state.patients_status or None,
            doctor_id=(
                int(st.session_state.patients_doctor_id)
                if st.session_state.get("patients_doctor_id")
                else None
            ),
        )
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)
        if st.button("Retry"):
            st.rerun()
        return

    render_patient_stats(data.get("counts"))
    items = data.get("items") or []
    render_patients_table(items)

    total_pages = max(int(data.get("total_pages") or 1), 1)
    page = int(data.get("page") or 1)
    total = int(data.get("total") or 0)

    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button("← Previous", disabled=page <= 1, use_container_width=True):
            st.session_state.patients_page = max(page - 1, 1)
            st.rerun()
    with nav2:
        st.markdown(
            f'<div class="pagination-meta">Page <b>{page}</b> of <b>{total_pages}</b>'
            f" · {total} total</div>",
            unsafe_allow_html=True,
        )
    with nav3:
        if st.button("Next →", disabled=page >= total_pages, use_container_width=True):
            st.session_state.patients_page = min(page + 1, total_pages)
            st.rerun()

    if not items:
        return

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<p class="panel-label">Patient actions</p>', unsafe_allow_html=True)

    ids = [int(item["id"]) for item in items]
    selected_id = st.selectbox(
        "Select patient",
        options=ids,
        format_func=lambda pid: next(
            (
                f"{item['full_name']} (#{item['id']})"
                for item in items
                if int(item["id"]) == pid
            ),
            str(pid),
        ),
    )

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("View", use_container_width=True):
            st.session_state.patients_ui_mode = "view"
            st.session_state.selected_patient_id = selected_id
            st.rerun()
    with a2:
        if st.button("Edit", use_container_width=True):
            st.session_state.patients_ui_mode = "edit"
            st.session_state.selected_patient_id = selected_id
            st.rerun()
    with a3:
        selected = next(item for item in items if int(item["id"]) == selected_id)
        new_status = "inactive" if selected.get("status") == "active" else "active"
        if st.button(f"Mark {new_status}", use_container_width=True):
            try:
                result = patients_api.update_patient(selected_id, {"status": new_status})
                st.success(result.get("message", "Status updated."))
                st.rerun()
            except ApiError as exc:
                if _handle_auth_error(exc):
                    return
                st.error(exc.detail)
    with a4:
        if st.button("Delete", type="primary", use_container_width=True):
            st.session_state.patients_ui_mode = "delete_confirm"
            st.session_state.selected_patient_id = selected_id
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_create() -> None:
    """Render create-patient form."""
    render_page_header("Add patient", subtitle="Create a new patient record.")
    if st.button("← Back to list"):
        set_patients_list_mode()
        st.rerun()

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    payload = render_patient_form(mode="create", form_key="create_patient_form")
    st.markdown("</div>", unsafe_allow_html=True)
    if payload is None:
        return

    try:
        result = patients_api.create_patient(payload)
        st.success(result.get("message", "Patient created successfully."))
        st.session_state.patients_page = 1
        set_patients_list_mode()
        st.rerun()
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)


def _load_selected_patient() -> dict | None:
    """Load the currently selected patient detail."""
    patient_id = st.session_state.selected_patient_id
    if patient_id is None:
        st.warning("No patient selected.")
        set_patients_list_mode()
        return None

    try:
        return patients_api.get_patient(int(patient_id))
    except ApiError as exc:
        if _handle_auth_error(exc):
            return None
        st.error(exc.detail)
        if st.button("Back to list"):
            set_patients_list_mode()
            st.rerun()
        return None


def _render_edit() -> None:
    """Render edit-patient form."""
    render_page_header("Edit patient", subtitle="Update an existing patient record.")
    if st.button("← Back to list"):
        set_patients_list_mode()
        st.rerun()

    patient = _load_selected_patient()
    if patient is None:
        return

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    payload = render_patient_form(
        mode="edit",
        patient=patient,
        form_key=f"edit_patient_form_{patient['id']}",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if payload is None:
        return

    try:
        result = patients_api.update_patient(int(patient["id"]), payload)
        st.success(result.get("message", "Patient updated successfully."))
        set_patients_list_mode()
        st.rerun()
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)


def _render_view() -> None:
    """Render read-only patient detail."""
    render_page_header("Patient details", subtitle="Read-only patient record.")
    if st.button("← Back to list"):
        set_patients_list_mode()
        st.rerun()

    patient = _load_selected_patient()
    if patient is None:
        return
    render_patient_detail(patient)


def _render_delete_confirm() -> None:
    """Confirm and delete a patient."""
    render_page_header("Delete patient", subtitle="This action cannot be undone.")
    patient_id = st.session_state.selected_patient_id
    st.warning(f"Delete patient #{patient_id}? This permanently removes the record.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            set_patients_list_mode()
            st.rerun()
    with col2:
        if st.button("Confirm delete", type="primary", use_container_width=True):
            try:
                result = patients_api.delete_patient(int(patient_id))
                st.success(result.get("message", "Patient deleted successfully."))
                set_patients_list_mode()
                st.rerun()
            except ApiError as exc:
                if _handle_auth_error(exc):
                    return
                st.error(exc.detail)


def render_patients() -> None:
    """Main patients view router based on session UI mode."""
    mode = st.session_state.patients_ui_mode
    if mode == "create":
        _render_create()
    elif mode == "edit":
        _render_edit()
    elif mode == "view":
        _render_view()
    elif mode == "delete_confirm":
        _render_delete_confirm()
    else:
        _render_list()
