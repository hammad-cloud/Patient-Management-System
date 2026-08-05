"""Login view — split-screen admin authentication."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from api import auth as auth_api
from api.client import ApiError
from config.settings import get_settings
from utils.session import set_auth_token
from utils.validators import validate_login

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
HOSPITAL_IMAGE = ASSETS_DIR / "hospital-login.jpg"


def _image_data_uri(path: Path) -> str:
    """Encode a local image as a data URI for inline HTML."""
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _inject_styles() -> None:
    """Style the two Streamlit columns into a full-viewport split login."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Manrope:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=block');

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer,
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
  display: none !important;
}

/* Hide "Press Enter to submit form" hint under inputs */
[data-testid="InputInstructions"] {
  display: none !important;
}

/* Show Material eye icon instead of raw "visibility" text */
[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
.material-symbols-outlined {
  font-family: "Material Symbols Outlined" !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 1.25rem !important;
  line-height: 1 !important;
  letter-spacing: normal !important;
  text-transform: none !important;
  display: inline-block !important;
  white-space: nowrap !important;
  word-wrap: normal !important;
  direction: ltr !important;
  -webkit-font-smoothing: antialiased;
  font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
}

.stApp, .stApp > header {
  background: #f3f7f6 !important;
}

section.main {
  padding: 0 !important;
}

div.block-container {
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
}

/* Keep the split row glued edge-to-edge */
div[data-testid="stHorizontalBlock"] {
  gap: 0 !important;
  align-items: stretch !important;
}

div[data-testid="stHorizontalBlock"] > div {
  padding: 0 !important;
}

/* LEFT column — image panel */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
  background: #0b1c24;
}

.login-hero {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
  background: #0b1c24;
}

.login-hero img {
  width: 100%;
  height: 100vh;
  object-fit: cover;
  display: block;
}

.login-hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(8, 24, 32, 0.18) 0%, rgba(8, 24, 32, 0.78) 100%),
    linear-gradient(90deg, rgba(8, 24, 32, 0.05) 0%, rgba(8, 24, 32, 0.35) 100%);
  pointer-events: none;
}

.login-hero-copy {
  position: absolute;
  left: 2.4rem;
  right: 2.4rem;
  bottom: 2.8rem;
  z-index: 2;
  color: #f4faf9;
  font-family: "Manrope", sans-serif;
}

.login-hero-copy .brand {
  margin: 0 0 0.7rem 0;
  font-family: "Fraunces", Georgia, serif;
  font-size: clamp(1.9rem, 3.2vw, 2.85rem);
  font-weight: 700;
  line-height: 1.12;
  letter-spacing: -0.02em;
  color: #ffffff !important;
}

.login-hero-copy .tagline {
  margin: 0;
  max-width: 26rem;
  font-size: 1rem;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.9) !important;
}

/* RIGHT column — form panel */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
  background:
    radial-gradient(circle at top right, rgba(15, 118, 110, 0.12), transparent 45%),
    linear-gradient(165deg, #f7faf9 0%, #eef5f3 55%, #e8f0ed 100%) !important;
  min-height: 100vh;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  padding: 2.75rem 2.25rem !important;
  box-sizing: border-box;
}

.login-heading .eyebrow {
  display: inline-block;
  margin-bottom: 0.75rem;
  color: #0f766e !important;
  font-family: "Manrope", sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.login-heading h1 {
  margin: 0 0 0.4rem 0;
  color: #102a33 !important;
  font-family: "Fraunces", Georgia, serif;
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.login-heading .subtitle {
  margin: 0 0 1.35rem 0;
  color: #5b6f78 !important;
  font-family: "Manrope", sans-serif;
  font-size: 0.98rem;
  line-height: 1.5;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stForm"] {
  border: 1px solid rgba(16, 42, 51, 0.08) !important;
  border-radius: 18px !important;
  padding: 1.25rem 1.15rem 1.05rem !important;
  background: rgba(255, 255, 255, 0.9) !important;
  box-shadow: 0 16px 36px rgba(16, 42, 51, 0.08);
  max-width: 420px;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) label,
div[data-testid="stHorizontalBlock"] > div:nth-child(2) p {
  color: #243b45 !important;
  font-family: "Manrope", sans-serif;
}

/* Do not force Manrope on icon glyphs (password eye uses Material Symbols) */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) span:not([data-testid="stIconMaterial"]) {
  color: #243b45 !important;
  font-family: "Manrope", sans-serif;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stIconMaterial"] {
  font-family: "Material Symbols Outlined" !important;
  color: #5b6f78 !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) label {
  font-weight: 600 !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
  background: #0f766e !important;
  border: 0 !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
  height: 2.85rem !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
  background: #0d9488 !important;
  color: #ffffff !important;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stAlert"] {
  max-width: 420px;
}

@media (max-width: 900px) {
  .login-hero, .login-hero img { min-height: 34vh; height: 34vh; }
  .login-hero-copy { left: 1.2rem; right: 1.2rem; bottom: 1.1rem; }
  div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
    min-height: auto;
    padding: 1.5rem 1rem 2rem !important;
  }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_login() -> None:
    """Render a professional split-screen admin login."""
    settings = get_settings()
    _inject_styles()

    left, right = st.columns([1.2, 1])

    with left:
        if not HOSPITAL_IMAGE.exists():
            st.error("Missing assets/hospital-login.jpg")
        else:
            image_uri = _image_data_uri(HOSPITAL_IMAGE)
            st.markdown(
                f"""
                <div class="login-hero">
                  <img src="{image_uri}" alt="Hospital building" />
                  <div class="login-hero-overlay"></div>
                  <div class="login-hero-copy">
                    <p class="brand">{settings.app_name}</p>
                    <p class="tagline">
                      Centralized records for doctors, patients, and hospital staff —
                      secure admin access for your care operations.
                    </p>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            """
            <div class="login-heading">
              <span class="eyebrow">Admin access</span>
              <h1>Sign in</h1>
              <p class="subtitle">Use your admin credentials to open the patient workspace.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False, border=False):
            email = st.text_input(
                "Email",
                value="admin123@gmail.com",
                autocomplete="username",
                placeholder="admin@hospital.com",
            )
            password = st.text_input(
                "Password",
                type="password",
                autocomplete="current-password",
                placeholder="Enter your password",
            )
            submitted = st.form_submit_button(
                "Sign in",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            errors = validate_login(email, password)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    token_payload = auth_api.login(email.strip(), password)
                    set_auth_token(token_payload["access_token"])
                    st.success("Signed in successfully.")
                    st.rerun()
                except ApiError as exc:
                    st.error(exc.detail)
