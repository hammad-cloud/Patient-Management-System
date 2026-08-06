"""Staff workspace — list, create, edit, view, delete."""

from __future__ import annotations

import streamlit as st

from api import staff as staff_api
from api.client import ApiError
from components.layout import render_page_header
from components.staff_form import render_staff_form
from components.staff_table import (
    render_staff_detail,
    render_staff_stats,
    render_staff_table,
)
from utils.session import clear_auth, set_staff_list_mode

SHIFT_FILTER_OPTIONS = ["", "morning", "evening", "night"]


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

    col1, col2, col3, col4 = st.columns([2, 1.2, 1.1, 0.9])
    with col1:
        st.session_state.staff_search = st.text_input(
            "Search",
            value=st.session_state.staff_search,
            placeholder="Name, role, email, or phone",
            label_visibility="collapsed",
        )
    with col2:
        st.session_state.staff_role = st.text_input(
            "Role filter",
            value=st.session_state.staff_role,
            placeholder="Filter by role",
            label_visibility="collapsed",
        )
    with col3:
        current_shift = st.session_state.staff_shift
        st.session_state.staff_shift = st.selectbox(
            "Shift",
            options=SHIFT_FILTER_OPTIONS,
            index=(
                SHIFT_FILTER_OPTIONS.index(current_shift)
                if current_shift in SHIFT_FILTER_OPTIONS
                else 0
            ),
            format_func=lambda v: "All shifts" if v == "" else v.capitalize(),
            label_visibility="collapsed",
        )
    with col4:
        limit_options = [10, 25, 50, 100]
        current_limit = st.session_state.staff_limit
        st.session_state.staff_limit = st.selectbox(
            "Rows",
            options=limit_options,
            index=limit_options.index(current_limit) if current_limit in limit_options else 0,
            format_func=lambda v: f"{v} rows",
            label_visibility="collapsed",
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_list() -> None:
    """Render the staff list with actions."""
    header_left, header_right = st.columns([3.2, 1])
    with header_left:
        render_page_header(
            "Staff",
            subtitle="Manage hospital staff roles, shifts, and salaries.",
        )
    with header_right:
        st.write("")
        st.write("")
        if st.button("Add staff", type="primary", use_container_width=True, key="add_staff"):
            st.session_state.staff_ui_mode = "create"
            st.rerun()

    _render_filters()

    try:
        data = staff_api.list_staff(
            page=st.session_state.staff_page,
            limit=st.session_state.staff_limit,
            search=st.session_state.staff_search or None,
            role=st.session_state.staff_role or None,
            shift=st.session_state.staff_shift or None,
        )
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)
        if st.button("Retry", key="staff_retry"):
            st.rerun()
        return

    render_staff_stats(int(data.get("total") or 0))
    items = data.get("items") or []
    render_staff_table(items)

    total_pages = max(int(data.get("total_pages") or 1), 1)
    page = int(data.get("page") or 1)
    total = int(data.get("total") or 0)

    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button(
            "← Previous",
            disabled=page <= 1,
            use_container_width=True,
            key="staff_prev",
        ):
            st.session_state.staff_page = max(page - 1, 1)
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
            key="staff_next",
        ):
            st.session_state.staff_page = min(page + 1, total_pages)
            st.rerun()

    if not items:
        return

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<p class="panel-label">Staff actions</p>', unsafe_allow_html=True)

    ids = [int(item["id"]) for item in items]
    selected_id = st.selectbox(
        "Select staff",
        options=ids,
        format_func=lambda sid: next(
            (
                f"{item['full_name']} — {item['role']} (#{item['id']})"
                for item in items
                if int(item["id"]) == sid
            ),
            str(sid),
        ),
        key="staff_select",
    )

    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("View", use_container_width=True, key="staff_view"):
            st.session_state.staff_ui_mode = "view"
            st.session_state.selected_staff_id = selected_id
            st.rerun()
    with a2:
        if st.button("Edit", use_container_width=True, key="staff_edit"):
            st.session_state.staff_ui_mode = "edit"
            st.session_state.selected_staff_id = selected_id
            st.rerun()
    with a3:
        if st.button("Delete", type="primary", use_container_width=True, key="staff_delete"):
            st.session_state.staff_ui_mode = "delete_confirm"
            st.session_state.selected_staff_id = selected_id
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_create() -> None:
    """Render create-staff form."""
    render_page_header("Add staff", subtitle="Create a new staff member profile.")
    if st.button("← Back to list", key="staff_create_back"):
        set_staff_list_mode()
        st.rerun()

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    payload = render_staff_form(mode="create", form_key="create_staff_form")
    st.markdown("</div>", unsafe_allow_html=True)
    if payload is None:
        return

    try:
        result = staff_api.create_staff(payload)
        st.success(result.get("message", "Staff created successfully."))
        st.session_state.staff_page = 1
        set_staff_list_mode()
        st.rerun()
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)


def _load_selected_staff() -> dict | None:
    """Load the currently selected staff detail."""
    staff_id = st.session_state.selected_staff_id
    if staff_id is None:
        st.warning("No staff member selected.")
        set_staff_list_mode()
        return None

    try:
        return staff_api.get_staff(int(staff_id))
    except ApiError as exc:
        if _handle_auth_error(exc):
            return None
        st.error(exc.detail)
        if st.button("Back to list", key="staff_load_back"):
            set_staff_list_mode()
            st.rerun()
        return None


def _render_edit() -> None:
    """Render edit-staff form."""
    render_page_header("Edit staff", subtitle="Update an existing staff profile.")
    if st.button("← Back to list", key="staff_edit_back"):
        set_staff_list_mode()
        st.rerun()

    staff = _load_selected_staff()
    if staff is None:
        return

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    payload = render_staff_form(
        mode="edit",
        staff=staff,
        form_key=f"edit_staff_form_{staff['id']}",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if payload is None:
        return

    try:
        result = staff_api.update_staff(int(staff["id"]), payload)
        st.success(result.get("message", "Staff updated successfully."))
        set_staff_list_mode()
        st.rerun()
    except ApiError as exc:
        if _handle_auth_error(exc):
            return
        st.error(exc.detail)


def _render_view() -> None:
    """Render read-only staff detail."""
    render_page_header("Staff details", subtitle="Read-only staff profile.")
    if st.button("← Back to list", key="staff_view_back"):
        set_staff_list_mode()
        st.rerun()

    staff = _load_selected_staff()
    if staff is None:
        return
    render_staff_detail(staff)


def _render_delete_confirm() -> None:
    """Confirm and delete a staff member."""
    render_page_header("Delete staff", subtitle="This action cannot be undone.")
    staff_id = st.session_state.selected_staff_id
    st.warning(f"Delete staff #{staff_id}? This permanently removes the record.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True, key="staff_delete_cancel"):
            set_staff_list_mode()
            st.rerun()
    with col2:
        if st.button(
            "Confirm delete",
            type="primary",
            use_container_width=True,
            key="staff_delete_confirm",
        ):
            try:
                result = staff_api.delete_staff(int(staff_id))
                st.success(result.get("message", "Staff deleted successfully."))
                set_staff_list_mode()
                st.rerun()
            except ApiError as exc:
                if _handle_auth_error(exc):
                    return
                st.error(exc.detail)


def render_staff() -> None:
    """Main staff view router based on session UI mode."""
    mode = st.session_state.staff_ui_mode
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
