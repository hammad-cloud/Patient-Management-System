"""Patient list / detail display helpers."""

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


def _render_html(markup: str) -> None:
    """Render HTML without Markdown treating indented tags as a code block."""
    st.markdown(markup.strip(), unsafe_allow_html=True)


def _doctor_label(item: dict[str, Any]) -> str:
    """Build a readable assigned-doctor label."""
    doctor = item.get("doctor") or {}
    if doctor.get("full_name"):
        specialization = doctor.get("specialization") or ""
        suffix = f" — {specialization}" if specialization else ""
        return f"{doctor['full_name']}{suffix}"
    if item.get("doctor_id"):
        return f"Doctor #{item['doctor_id']}"
    return "—"


def render_patient_stats(counts: dict[str, Any] | None) -> None:
    """Show summary metrics for patients as polished cards."""
    counts = counts or {}
    all_count = int(counts.get("all", 0) or 0)
    active_count = int(counts.get("active", 0) or 0)

    _render_html(
        f"""
<div class="metric-grid">
  <div class="metric-card">
    <p class="label">All patients</p>
    <p class="value">{all_count}</p>
  </div>
  <div class="metric-card active">
    <p class="label">Active patients</p>
    <p class="value">{active_count}</p>
  </div>
</div>
"""
    )


def render_patients_table(items: list[dict[str, Any]]) -> None:
    """Render a professional HTML patients table with status pills."""
    if not items:
        _render_html(
            '<div class="empty-state">No patients match your current filters.</div>'
        )
        return

    rows_html: list[str] = []
    for item in items:
        diseases = item.get("diseases") or []
        disease_text = ", ".join(str(d) for d in diseases) if diseases else "—"
        status = str(item.get("status") or "inactive").lower()
        status_class = "active" if status == "active" else "inactive"
        email = item.get("email") or "—"

        rows_html.append(
            "<tr>"
            f"<td>{escape(str(item.get('id', '')))}</td>"
            f"<td class='name-cell'>{escape(str(item.get('full_name', '')))}</td>"
            f"<td>{escape(str(item.get('age', '')))}</td>"
            f"<td>{escape(str(item.get('gender', '')).capitalize())}</td>"
            f"<td>{escape(_doctor_label(item))}</td>"
            f"<td>{escape(disease_text)}</td>"
            f"<td>{escape(str(item.get('phone', '')))}</td>"
            f"<td>{escape(str(email))}</td>"
            f"<td><span class='status-pill {status_class}'>{escape(status)}</span></td>"
            "</tr>"
        )

    _render_html(
        "<div class='patients-table-wrap'>"
        "<table class='patients-table'>"
        "<thead><tr>"
        "<th>ID</th><th>Name</th><th>Age</th><th>Gender</th><th>Doctor</th>"
        "<th>Diseases</th><th>Phone</th><th>Email</th><th>Status</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table></div>"
    )


def render_patient_detail(patient: dict[str, Any]) -> None:
    """Render a read-only patient detail card."""
    diseases = patient.get("diseases") or []
    disease_text = ", ".join(str(d) for d in diseases) if diseases else "—"
    status = str(patient.get("status") or "inactive").lower()
    status_class = "active" if status == "active" else "inactive"

    _render_html(
        f"""
<div class="detail-card">
  <h3>{escape(str(patient.get("full_name", "")))}</h3>
  <div class="detail-grid">
    <div class="detail-item">
      <span class="label">ID</span>
      <span class="value">{escape(str(patient.get("id", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Status</span>
      <span class="value"><span class="status-pill {status_class}">{escape(status)}</span></span>
    </div>
    <div class="detail-item">
      <span class="label">Age</span>
      <span class="value">{escape(str(patient.get("age", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Gender</span>
      <span class="value">{escape(str(patient.get("gender", "")).capitalize())}</span>
    </div>
    <div class="detail-item">
      <span class="label">Assigned doctor</span>
      <span class="value">{escape(_doctor_label(patient))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Phone</span>
      <span class="value">{escape(str(patient.get("phone", "")))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Email</span>
      <span class="value">{escape(str(patient.get("email") or "—"))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Address</span>
      <span class="value">{escape(str(patient.get("address") or "—"))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Diseases</span>
      <span class="value">{escape(disease_text)}</span>
    </div>
    <div class="detail-item">
      <span class="label">Created</span>
      <span class="value">{escape(str(patient.get("created_at") or "—"))}</span>
    </div>
    <div class="detail-item">
      <span class="label">Updated</span>
      <span class="value">{escape(str(patient.get("updated_at") or "—"))}</span>
    </div>
  </div>
  <div class="detail-item" style="margin-top:1.1rem;">
    <span class="label">Medical history</span>
    <span class="value">{escape(str(patient.get("medical_history") or "—"))}</span>
  </div>
</div>
"""
    )
