# Patient Management System — Streamlit Frontend

Python Streamlit UI that talks to the FastAPI backend.

## Folder structure

```text
streamlit/
├── app.py                 # Entry point (routing + page config)
├── requirements.txt
├── .env.example
├── .streamlit/
│   └── config.toml        # Theme & server settings
├── config/
│   └── settings.py        # Env-based configuration
├── api/
│   ├── client.py          # Shared HTTP client + errors
│   ├── auth.py            # Login / logout API calls
│   └── patients.py        # Patient CRUD API calls
├── components/
│   ├── layout.py          # Sidebar + page header
│   ├── patient_form.py    # Create / edit form
│   └── patient_table.py   # Table, stats, detail view
├── views/
│   ├── login.py           # Login screen
│   └── patients.py        # Patients workspace
└── utils/
    ├── session.py         # Session-state helpers
    └── validators.py      # Client-side validation
```

## Setup

```powershell
cd "D:\Patient Management System\streamlit"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Run

1. Start the FastAPI backend first (`uvicorn app.main:app --reload` from `backend`).
2. Then run Streamlit:

```powershell
streamlit run app.py
```

Open: http://localhost:8501

## Default admin login

- Email: `admin123@gmail.com`
- Password: `12345678`

## Features (ported from React)

- Admin login / logout (JWT in `st.session_state`)
- Patient list with search, gender/status filters, pagination
- Create / edit / view / delete patients
- Toggle active / inactive status
