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
│   ├── patients.py        # Patient CRUD API calls
│   ├── doctors.py         # Doctor CRUD API calls
│   └── staff.py           # Staff CRUD API calls
├── assets/
│   └── hospital-login.jpg # Login screen image
├── components/
│   ├── layout.py          # Sidebar + page header
│   ├── workspace_styles.py# Shared workspace CSS
│   ├── patient_form.py    # Patient create / edit form
│   ├── patient_table.py   # Patient table, stats, detail view
│   ├── doctor_form.py     # Doctor create / edit form
│   ├── doctor_table.py    # Doctor table, stats, detail view
│   ├── staff_form.py      # Staff create / edit form
│   └── staff_table.py     # Staff table, stats, detail view
├── views/
│   ├── login.py           # Login screen
│   ├── patients.py        # Patients workspace
│   ├── doctors.py         # Doctors workspace
│   └── staff.py           # Staff workspace
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

## Features

- Admin login / logout (JWT in `st.session_state`)
- Patient list with search, gender/status filters, pagination
- Create / edit / view / delete patients, toggle active / inactive status
- Doctors workspace: create / edit / view / delete doctors
- Staff workspace: create / edit / view / delete staff with role and shift
