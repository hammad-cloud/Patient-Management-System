"""Shared layout helpers (header, sidebar navigation, sign-out)."""

from __future__ import annotations

import streamlit as st

from api import auth as auth_api
from api.client import ApiError
from config.settings import get_settings
from utils.session import (
    PAGE_DOCTORS,
    PAGE_PATIENTS,
    PAGE_STAFF,
    clear_auth,
    set_current_page,
)


def render_sidebar() -> None:
    """Render authenticated sidebar with brand, nav, and sign-out."""
    settings = get_settings()
    current = st.session_state.get("current_page", PAGE_PATIENTS)

    with st.sidebar:
        st.markdown(
            f"""
<div class="sidebar-brand">
  <span class="eyebrow">Hospital admin</span>
  <h2>{settings.app_name}</h2>
  <p>Manage doctors, patients, and staff from one secure workspace.</p>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(
            '<p class="panel-label" style="color:#5eead4 !important;">Navigation</p>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Patients",
            use_container_width=True,
            type="primary" if current == PAGE_PATIENTS else "secondary",
            key="nav_patients",
        ):
            if current != PAGE_PATIENTS:
                set_current_page(PAGE_PATIENTS)
                st.rerun()

        if st.button(
            "Doctors",
            use_container_width=True,
            type="primary" if current == PAGE_DOCTORS else "secondary",
            key="nav_doctors",
        ):
            if current != PAGE_DOCTORS:
                set_current_page(PAGE_DOCTORS)
                st.rerun()

        if st.button(
            "Staff",
            use_container_width=True,
            type="primary" if current == PAGE_STAFF else "secondary",
            key="nav_staff",
        ):
            if current != PAGE_STAFF:
                set_current_page(PAGE_STAFF)
                st.rerun()

        st.divider()

        if st.button("Sign out", use_container_width=True, type="secondary", key="nav_sign_out"):
            try:
                auth_api.logout()
            except ApiError:
                pass
            clear_auth()
            st.rerun()


def render_page_header(
    title: str,
    *,
    subtitle: str | None = None,
    eyebrow: str = "Admin workspace",
) -> None:
    """Render a consistent page title block."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="page-header">
          <div class="copy">
            <span class="eyebrow">{eyebrow}</span>
            <h1>{title}</h1>
            {subtitle_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
