"""Doctors workspace — list, create, edit, view, delete."""

from __future__ import annotations

import streamlit as st

from api import doctors as doctors_api
from api.client import ApiError
from components.doctor_form import render_doctor_form
from components.doctor_table import (
    render_doctor_detail,
    render_doctor_stats,
    render_doctors_table,
)
from components.layout import render_page_header
from utils.session import clear_auth, set_doctors_list_mode


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
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<p class="panel-label">Search & filters</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2.4, 1.4, 1])
    with col1:
        st.session_state.doctors_search = st.text_input(
            "Search",
            value=st.session_state.doctors_search,
            placeholder="Name, email, or specialization",
            label_visibility="collapsed",
        )
    with col2:
        st.session_state.doctors_specialization = st.text_input(
            "Specialization filter",
            value=st.session_state.doctors_specialization,
            placeholder="Filter specialization",
            label_visibility="collapsed",
        )
    with col3:
        limit_options = [10, 25, 50, 100]
        current_limit = st.session_state.doctors_limit
        st.session_state.doctors_limit = st.selectbox(
            "Rows",
            options=limit_options,
            index=limit_options.index(current_limit) if current_limit in limit_options else 0,
            format_func=lambda v: f"{v} rows",
            label_visibility="collapsed",
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_list() -> None:
    """Render the doctors list with actions."""
    header_left, header_right = st.columns([3.2, 1])
    with header_left:
        render_page_header(
            "Doctors",
            subtitle="Manage doctor profiles, specializations, and contact details.",
        )
    with header_right:
        st.write("")
        st.write("")
        if st.button("Add doctor", type="primary", use_container_width=True, key="add_doctor"):
            st.session_state.doctors_ui_mode = "create"
            st.rerun()

    _render_filters()

    try:
        data = doctors_api.list_doctors(
            page=st.session_state.doctors_page,
            limit=st.session_state.doctors_limit,
            search=st.session_state.doctors_search or None,
            specialization=st.session_state.doctors_specialization or None,
        )
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)
        if st.button("Retry", key="doctors_retry"):
            st.rerun()
        return

    render_doctor_stats(int(data.get("total") or 0))
    items = data.get("items") or []
    render_doctors_table(items)

    total_pages = max(int(data.get("total_pages") or 1), 1)
    page = int(data.get("page") or 1)
    total = int(data.get("total") or 0)

    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button(
            "← Previous",
            disabled=page <= 1,
            use_container_width=True,
            key="doctors_prev",
        ):
            st.session_state.doctors_page = max(page - 1, 1)
            st.rerun()
    with nav2:
        st.markdown(
            f'<div class="pagination-meta">Page <b>{page}</b> of <b>{total_pages}</b>'
            f" · {total} total</div>",
            unsafe_allow_html=True,
        )
    with nav3:
        if st.button(
            "Next →",
            disabled=page >= total_pages,
            use_container_width=True,
            key="doctors_next",
        ):
            st.session_state.doctors_page = min(page + 1, total_pages)
            st.rerun()

    if not items:
        return

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<p class="panel-label">Doctor actions</p>', unsafe_allow_html=True)

    ids = [int(item["id"]) for item in items]
    selected_id = st.selectbox(
        "Select doctor",
        options=ids,
        format_func=lambda did: next(
            (
                f"{item['full_name']} — {item['specialization']} (#{item['id']})"
                for item in items
                if int(item["id"]) == did
            ),
            str(did),
        ),
        key="doctors_select",
    )

    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("View", use_container_width=True, key="doctor_view"):
            st.session_state.doctors_ui_mode = "view"
            st.session_state.selected_doctor_id = selected_id
            st.rerun()
    with a2:
        if st.button("Edit", use_container_width=True, key="doctor_edit"):
            st.session_state.doctors_ui_mode = "edit"
            st.session_state.selected_doctor_id = selected_id
            st.rerun()
    with a3:
        if st.button("Delete", type="primary", use_container_width=True, key="doctor_delete"):
            st.session_state.doctors_ui_mode = "delete_confirm"
            st.session_state.selected_doctor_id = selected_id
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_create() -> None:
    """Render create-doctor form."""
    render_page_header("Add doctor", subtitle="Create a new doctor profile.")
    if st.button("← Back to list", key="doctor_create_back"):
        set_doctors_list_mode()
        st.rerun()

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    payload = render_doctor_form(mode="create", form_key="create_doctor_form")
    st.markdown("</div>", unsafe_allow_html=True)
    if payload is None:
        return

    try:
        result = doctors_api.create_doctor(payload)
        st.success(result.get("message", "Doctor created successfully."))
        st.session_state.doctors_page = 1
        set_doctors_list_mode()
        st.rerun()
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)


def _load_selected_doctor() -> dict | None:
    """Load the currently selected doctor detail."""
    doctor_id = st.session_state.selected_doctor_id
    if doctor_id is None:
        st.warning("No doctor selected.")
        set_doctors_list_mode()
        return None

    try:
        return doctors_api.get_doctor(int(doctor_id))
    except ApiError as exc:
        if _handle_auth_error(exc):
            return None
        st.error(exc.detail)
        if st.button("Back to list", key="doctor_load_back"):
            set_doctors_list_mode()
            st.rerun()
        return None


def _render_edit() -> None:
    """Render edit-doctor form."""
    render_page_header("Edit doctor", subtitle="Update an existing doctor profile.")
    if st.button("← Back to list", key="doctor_edit_back"):
        set_doctors_list_mode()
        st.rerun()

    doctor = _load_selected_doctor()
    if doctor is None:
        return

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    payload = render_doctor_form(
        mode="edit",
        doctor=doctor,
        form_key=f"edit_doctor_form_{doctor['id']}",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if payload is None:
        return

    try:
        result = doctors_api.update_doctor(int(doctor["id"]), payload)
        st.success(result.get("message", "Doctor updated successfully."))
        set_doctors_list_mode()
        st.rerun()
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)


def _render_view() -> None:
    """Render read-only doctor detail."""
    render_page_header("Doctor details", subtitle="Read-only doctor profile.")
    if st.button("← Back to list", key="doctor_view_back"):
        set_doctors_list_mode()
        st.rerun()

    doctor = _load_selected_doctor()
    if doctor is None:
        return
    render_doctor_detail(doctor)


def _render_delete_confirm() -> None:
    """Confirm and delete a doctor."""
    render_page_header("Delete doctor", subtitle="This action cannot be undone.")
    doctor_id = st.session_state.selected_doctor_id
    st.warning(f"Delete doctor #{doctor_id}? This permanently removes the record.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True, key="doctor_delete_cancel"):
            set_doctors_list_mode()
            st.rerun()
    with col2:
        if st.button(
            "Confirm delete",
            type="primary",
            use_container_width=True,
            key="doctor_delete_confirm",
        ):
            try:
                result = doctors_api.delete_doctor(int(doctor_id))
                st.success(result.get("message", "Doctor deleted successfully."))
                set_doctors_list_mode()
                st.rerun()
            except ApiError as exc:
                if _handle_auth_error(exc):
                    return
                st.error(exc.detail)


def render_doctors() -> None:
    """Main doctors view router based on session UI mode."""
    mode = st.session_state.doctors_ui_mode
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
