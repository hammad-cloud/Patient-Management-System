"""Shared professional styles for the authenticated workspace."""

from __future__ import annotations

import streamlit as st

_WORKSPACE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Manrope:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=block');

html, body, [class*="css"] {
  font-family: "Manrope", sans-serif;
}

.stApp {
  background:
    radial-gradient(circle at top right, rgba(15, 118, 110, 0.08), transparent 36%),
    linear-gradient(180deg, #f4f8f7 0%, #eef3f2 100%);
}

/* Fully remove Streamlit toolbar / Deploy chrome (it reserves top space) */
[data-testid="stHeader"],
.stApp > header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
.stDeployButton,
#MainMenu,
footer {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  visibility: hidden !important;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
}

/* CSS-injection markdown must not consume vertical space */
[data-testid="stMarkdownContainer"]:has(> style),
[data-testid="stMarkdownContainer"]:has(style) {
  margin: 0 !important;
  padding: 0 !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  border: none !important;
}

/* Main page: kill default ~6rem top padding on every workspace page */
section.main,
[data-testid="stMain"],
[data-testid="stAppViewContainer"] {
  padding-top: 0 !important;
  margin-top: 0 !important;
}

div.block-container,
[data-testid="stMainBlockContainer"] {
  padding-top: 0.85rem !important;
  padding-bottom: 2rem !important;
  max-width: 100% !important;
}

[data-testid="InputInstructions"] {
  display: none !important;
}

[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"] {
  font-family: "Material Symbols Outlined" !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 1.2rem !important;
  line-height: 1 !important;
  font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #102a33 0%, #0b1c24 100%) !important;
  border-right: 1px solid rgba(255,255,255,0.06);
  top: 0 !important;
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* Remove sidebar header spacer (aligned with Deploy toolbar) */
[data-testid="stSidebarHeader"],
section[data-testid="stSidebar"] header {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
  border: none !important;
}

section[data-testid="stSidebar"] > div:first-child,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] .block-container {
  padding-top: 0.85rem !important;
  margin-top: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:first-of-type,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

section[data-testid="stSidebar"] * {
  color: #e8f2f0 !important;
}

section[data-testid="stSidebar"] .sidebar-brand {
  padding: 0 0.15rem 0.65rem;
  margin-top: 0;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:first-of-type,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:first-of-type p {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

section[data-testid="stSidebar"] .sidebar-brand .eyebrow {
  display: block;
  margin-bottom: 0.45rem;
  color: #5eead4 !important;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

section[data-testid="stSidebar"] .sidebar-brand h2 {
  margin: 0 0 0.4rem 0;
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.25;
  color: #ffffff !important;
}

section[data-testid="stSidebar"] .sidebar-brand p {
  margin: 0;
  color: rgba(232, 242, 240, 0.72) !important;
  font-size: 0.88rem;
  line-height: 1.45;
}

section[data-testid="stSidebar"] .stButton > button {
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.06) !important;
  color: #ffffff !important;
  font-weight: 600 !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
  border-color: #5eead4 !important;
  background: rgba(94, 234, 212, 0.12) !important;
  color: #ffffff !important;
}

/* Active nav item (Streamlit primary button in sidebar) */
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
  background: #0f766e !important;
  border-color: #0f766e !important;
  color: #ffffff !important;
}

section[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.12) !important;
}

/* Main header */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin: 0 0 1rem;
}

.page-header .copy .eyebrow {
  display: inline-block;
  margin-bottom: 0.4rem;
  color: #0f766e;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.page-header .copy h1 {
  margin: 0 0 0.35rem 0;
  font-family: "Fraunces", Georgia, serif;
  font-size: 2.1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #102a33;
}

.page-header .copy p {
  margin: 0;
  color: #5b6f78;
  font-size: 0.98rem;
}

/* Cards / panels */
.panel-card {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(16, 42, 51, 0.08);
  border-radius: 18px;
  padding: 1rem 1.1rem;
  box-shadow: 0 10px 28px rgba(16, 42, 51, 0.05);
  margin-bottom: 1rem;
}

.panel-label {
  margin: 0 0 0.75rem 0;
  color: #5b6f78;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Metric cards */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin: 0.2rem 0 1rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(16, 42, 51, 0.08);
  border-radius: 18px;
  padding: 1.05rem 1.15rem;
  box-shadow: 0 10px 28px rgba(16, 42, 51, 0.05);
}

.metric-card .label {
  margin: 0 0 0.35rem 0;
  color: #5b6f78;
  font-size: 0.82rem;
  font-weight: 600;
}

.metric-card .value {
  margin: 0;
  font-family: "Fraunces", Georgia, serif;
  font-size: 2rem;
  font-weight: 700;
  color: #102a33;
  letter-spacing: -0.02em;
}

.metric-card.active .value {
  color: #0f766e;
}

/* Table */
.patients-table-wrap {
  overflow-x: auto;
  border-radius: 18px;
  border: 1px solid rgba(16, 42, 51, 0.08);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 28px rgba(16, 42, 51, 0.05);
  margin-bottom: 1rem;
}

.patients-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
}

.patients-table th {
  text-align: left;
  padding: 0.85rem 1rem;
  background: #eef5f3;
  color: #3d5560;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(16, 42, 51, 0.08);
  white-space: nowrap;
}

.patients-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(16, 42, 51, 0.06);
  color: #243b45;
  vertical-align: middle;
}

.patients-table tr:last-child td {
  border-bottom: none;
}

.patients-table tr:hover td {
  background: rgba(15, 118, 110, 0.04);
}

.patients-table .name-cell {
  font-weight: 600;
  color: #102a33;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.22rem 0.65rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: capitalize;
}

.status-pill.active {
  background: rgba(15, 118, 110, 0.12);
  color: #0f766e;
}

.status-pill.inactive {
  background: rgba(100, 116, 139, 0.14);
  color: #475569;
}

.empty-state {
  text-align: center;
  padding: 2.2rem 1rem;
  color: #5b6f78;
  background: rgba(255,255,255,0.85);
  border: 1px dashed rgba(16, 42, 51, 0.14);
  border-radius: 18px;
}

/* Primary buttons in main area */
div.block-container .stButton > button[kind="primary"],
div.block-container .stButton > button[data-testid="baseButton-primary"] {
  background: #0f766e !important;
  border: none !important;
  color: #fff !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
}

div.block-container .stButton > button[kind="primary"]:hover,
div.block-container .stButton > button[data-testid="baseButton-primary"]:hover {
  background: #0d9488 !important;
  color: #fff !important;
}

div.block-container .stButton > button {
  border-radius: 12px !important;
  font-weight: 600 !important;
}

/* Detail card */
.detail-card {
  background: rgba(255,255,255,0.92);
  border: 1px solid rgba(16, 42, 51, 0.08);
  border-radius: 18px;
  padding: 1.25rem 1.35rem;
  box-shadow: 0 10px 28px rgba(16, 42, 51, 0.05);
}

.detail-card h3 {
  margin: 0 0 1rem 0;
  font-family: "Fraunces", Georgia, serif;
  color: #102a33;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem 1.25rem;
}

.detail-item .label {
  display: block;
  margin-bottom: 0.2rem;
  color: #5b6f78;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.detail-item .value {
  color: #102a33;
  font-size: 0.98rem;
  font-weight: 550;
}

.pagination-meta {
  text-align: center;
  padding-top: 0.55rem;
  color: #5b6f78;
  font-size: 0.92rem;
}

@media (max-width: 900px) {
  .metric-grid, .detail-grid {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
"""


def inject_workspace_styles() -> None:
    """Inject shared workspace styles without eating main-page top space."""
    # Keep <style> out of the main column — Streamlit wrappers create a top gap.
    st.sidebar.markdown(_WORKSPACE_CSS, unsafe_allow_html=True)
