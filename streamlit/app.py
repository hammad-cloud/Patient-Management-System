"""
Patient Management System — Streamlit entry point.

Run:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from components.layout import render_sidebar
from components.workspace_styles import inject_workspace_styles
from config.settings import get_settings
from utils.session import (
    PAGE_DOCTORS,
    PAGE_PATIENTS,
    PAGE_STAFF,
    init_session_state,
    is_authenticated,
)
from views.doctors import render_doctors
from views.login import render_login
from views.patients import render_patients
from views.staff import render_staff

settings = get_settings()

st.set_page_config(
    page_title=settings.app_name,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()


def main() -> None:
    """Route between login and authenticated workspace pages."""
    if not is_authenticated():
        render_login()
        return

    inject_workspace_styles()
    render_sidebar()

    page = st.session_state.get("current_page", PAGE_PATIENTS)
    if page == PAGE_DOCTORS:
        render_doctors()
    elif page == PAGE_STAFF:
        render_staff()
    else:
        render_patients()


if __name__ == "__main__":
    main()
else:
    main()
