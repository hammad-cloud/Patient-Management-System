"""Staff list / detail display helpers."""

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


def render_staff_stats(total: int) -> None:
    """Show summary metric for staff."""
    _render_html(
        f"""
<div class="metric-grid" style="grid-template-columns:1fr;">
  <div class="metric-card active">
    <p class="label">Total staff</p>
    <p class="value">{int(total or 0)}</p>
  </div>
</div>
"""
    )


def render_staff_table(items: list[dict[str, Any]]) -> None:
    """Render a professional HTML staff table with shift pills."""
    if not items:
        _render_html(
            '<div class="empty-state">No staff members match your current filters.</div>'
        )
        return

    rows_html: list[str] = []
    for item in items:
        shift = str(item.get("shift") or "").lower()
        rows_html.append(
            "<tr>"
            f"<td>{escape(str(item.get('id', '')))}</td>"
            f"<td class='name-cell'>{escape(str(item.get('full_name', '')))}</td>"
            f"<td>{escape(str(item.get('role', '')))}</td>"
            f"<td><span class='status-pill active'>{escape(shift.capitalize() if shift else '—')}</span></td>"
            f"<td>{escape(str(item.get('email', '') or '—'))}</td>"
            f"<td>{escape(str(item.get('phone', '') or '—'))}</td>"
            f"<td>{escape(_format_salary(item.get('salary')))}</td>"
            "</tr>"
        )

    _render_html(
        "<div class='patients-table-wrap'>"
        "<table class='patients-table'>"
        "<thead><tr>"
        "<th>ID</th><th>Name</th><th>Role</th><th>Shift</th>"
        "<th>Email</th><th>Phone</th><th>Salary</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table></div>"
    )


def render_staff_detail(staff: dict[str, Any]) -> None:
    """Render a read-only staff detail card."""
    shift = str(staff.get("shift") or "").lower()
    _render_html(
        f"""
<div class="detail-card">
  <h3>{escape(str(staff.get("full_name", "")))}</h3>
  <div class="detail-grid">
    <div class="detail-item">
      <span class="label">ID</span>
      <span class="value">{escape(str(staff.get("id", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Role</span>
      <span class="value">{escape(str(staff.get("role", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Shift</span>
      <span class="value"><span class="status-pill active">{escape(shift.capitalize() if shift else "—")}</span></span>
    </div>
    <div class="detail-item">
      <span class="label">Email</span>
      <span class="value">{escape(str(staff.get("email") or "—"))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Phone</span>
      <span class="value">{escape(str(staff.get("phone") or "—"))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Salary</span>
      <span class="value">{escape(_format_salary(staff.get("salary")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Created</span>
      <span class="value">{escape(str(staff.get("created_at") or "—"))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Updated</span>
      <span class="value">{escape(str(staff.get("updated_at") or "—"))}</span>
    </div>
  </div>
</div>
"""
    )
