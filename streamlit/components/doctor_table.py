"""Doctor list / detail display helpers."""

from __future__ import annotations

from html import escape
from typing import Any


def _render_html(markup: str) -> None:
    """Render HTML without Markdown treating indented tags as a code block."""
    import streamlit as st

    st.markdown(markup.strip(), unsafe_allow_html=True)


def _format_salary(value: Any) -> str:
    """Format salary for display."""
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value or "—")


def render_doctor_stats(total: int) -> None:
    """Show summary metric for doctors."""
    _render_html(
        f"""
<div class="metric-grid" style="grid-template-columns:1fr;">
  <div class="metric-card active">
    <p class="label">Total doctors</p>
    <p class="value">{int(total or 0)}</p>
  </div>
</div>
"""
    )


def render_doctors_table(items: list[dict[str, Any]]) -> None:
    """Render a professional HTML doctors table."""
    if not items:
        _render_html(
            '<div class="empty-state">No doctors match your current filters.</div>'
        )
        return

    rows_html: list[str] = []
    for item in items:
        rows_html.append(
            "<tr>"
            f"<td>{escape(str(item.get('id', '')))}</td>"
            f"<td class='name-cell'>{escape(str(item.get('full_name', '')))}</td>"
            f"<td>{escape(str(item.get('specialization', '')))}</td>"
            f"<td>{escape(str(item.get('email', '')))}</td>"
            f"<td>{escape(str(item.get('phone', '')))}</td>"
            f"<td>{escape(_format_salary(item.get('salary')))}</td>"
            "</tr>"
        )

    _render_html(
        "<div class='patients-table-wrap'>"
        "<table class='patients-table'>"
        "<thead><tr>"
        "<th>ID</th><th>Name</th><th>Specialization</th>"
        "<th>Email</th><th>Phone</th><th>Salary</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table></div>"
    )


def render_doctor_detail(doctor: dict[str, Any]) -> None:
    """Render a read-only doctor detail card."""
    _render_html(
        f"""
<div class="detail-card">
  <h3>{escape(str(doctor.get("full_name", "")))}</h3>
  <div class="detail-grid">
    <div class="detail-item">
      <span class="label">ID</span>
      <span class="value">{escape(str(doctor.get("id", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Specialization</span>
      <span class="value">{escape(str(doctor.get("specialization", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Email</span>
      <span class="value">{escape(str(doctor.get("email", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Phone</span>
      <span class="value">{escape(str(doctor.get("phone", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Salary</span>
      <span class="value">{escape(_format_salary(doctor.get("salary")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Created</span>
      <span class="value">{escape(str(doctor.get("created_at") or "—"))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Updated</span>
      <span class="value">{escape(str(doctor.get("updated_at") or "—"))}</span>
    </div>
  </div>
</div>
"""
    )
