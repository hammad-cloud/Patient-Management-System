# Patient Management System

A full-stack hospital administration app for managing **patients**, **doctors** and **staff**.
The backend is a REST API built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**; the frontend is a **Streamlit** dashboard that talks to it over HTTP using JWT authentication.

---

## Features

- **Authentication** — admin login / logout with JWT access tokens and a server-side token blacklist
- **Patients** — create, view, update and delete records; search, filter by gender / status / doctor, and paginate
- **Doctors** — full CRUD with specialization and contact details; assign doctors to patients
- **Staff** — full CRUD with role and shift management
- **Database migrations** with Alembic
- **Automated API tests** with pytest (in-memory SQLite, no Postgres needed)
- **Interactive API docs** via Swagger UI and ReDoc

## Tech Stack

| Layer      | Technology                                         |
|------------|----------------------------------------------------|
| Backend    | Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy     |
| Database   | PostgreSQL 16 (Docker), Alembic migrations         |
| Auth       | PyJWT (HS256), bcrypt password hashing             |
| Frontend   | Streamlit, httpx, pandas                           |
| Testing    | pytest, httpx (FastAPI TestClient)                 |

## Project Structure

```text
Patient-Management-System/
├── backend/                        # FastAPI REST API
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   │   └── 001_initial_schema.py
│   │   └── env.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py             # Shared dependencies (DB session, current user)
│   │   │   └── v1/
│   │   │       ├── router.py       # Aggregates all v1 routers
│   │   │       └── endpoints/      # auth, doctors, patients, staff
│   │   ├── core/
│   │   │   ├── config.py           # Environment-based settings
│   │   │   └── security.py         # Password hashing & JWT helpers
│   │   ├── crud/                   # Database operations per model
│   │   ├── db/                     # Engine, session and Base
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   └── main.py                 # Application entry point
│   ├── tests/
│   │   ├── api/                    # Endpoint tests
│   │   └── conftest.py             # Test fixtures (SQLite in-memory)
│   ├── alembic.ini
│   ├── pytest.ini
│   ├── requirements.txt
│   └── .env.example
├── streamlit/                      # Streamlit frontend
│   ├── api/                        # HTTP client for the backend
│   ├── assets/                     # Static images
│   ├── components/                 # Reusable UI (forms, tables, layout)
│   ├── config/                     # Frontend settings
│   ├── utils/                      # Session state & validators
│   ├── views/                      # Pages: login, patients, doctors, staff
│   ├── .streamlit/config.toml      # Theme & server settings
│   ├── app.py                      # Frontend entry point
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml              # Local PostgreSQL
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Docker Desktop (for PostgreSQL)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/hammad-cloud/Patient-Management-System.git
cd Patient-Management-System
```

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

### 3. Set up the backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

The API runs at **http://127.0.0.1:8000**.

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 4. Set up the frontend

Open a new terminal from the project root:

```bash
cd streamlit
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**.

### Default admin login

| Email                | Password   |
|----------------------|------------|
| `admin123@gmail.com` | `12345678` |

> Change `ADMIN_EMAIL`, `ADMIN_PASSWORD` and `SECRET_KEY` in `backend/.env` before deploying anywhere.

## Environment Variables

**backend/.env**

| Variable                      | Description                         |
|-------------------------------|-------------------------------------|
| `APP_NAME`                    | Application name                    |
| `DATABASE_URL`                | SQLAlchemy database URL             |
| `SECRET_KEY`                  | Secret used to sign JWTs            |
| `ALGORITHM`                   | JWT algorithm (default `HS256`)     |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes           |
| `ADMIN_EMAIL`                 | Seeded admin account email          |
| `ADMIN_PASSWORD`              | Seeded admin account password       |

**streamlit/.env**

| Variable                  | Description                     |
|---------------------------|---------------------------------|
| `APP_NAME`                | Title shown in the UI           |
| `API_BASE_URL`            | Backend base URL (`/api/v1`)    |
| `REQUEST_TIMEOUT_SECONDS` | HTTP request timeout            |

## API Endpoints

All routes are prefixed with `/api/v1`. Every route except login requires a `Bearer` token.

| Method | Endpoint                 | Description                                  |
|--------|--------------------------|----------------------------------------------|
| POST   | `/auth/login`            | Log in and receive an access token           |
| POST   | `/auth/logout`           | Revoke the current token                     |
| GET    | `/patients/`             | List patients (search, filters, pagination)  |
| POST   | `/patients/`             | Create a patient                             |
| GET    | `/patients/{id}`         | Get a patient                                |
| PATCH  | `/patients/{id}`         | Update a patient                             |
| DELETE | `/patients/{id}`         | Delete a patient                             |
| GET    | `/doctors/`              | List doctors                                 |
| POST   | `/doctors/`              | Create a doctor                              |
| GET    | `/doctors/{id}`          | Get a doctor                                 |
| PUT    | `/doctors/{id}`          | Update a doctor                              |
| DELETE | `/doctors/{id}`          | Delete a doctor                              |
| GET    | `/staff/`                | List staff                                   |
| POST   | `/staff/`                | Create a staff member                        |
| GET    | `/staff/{id}`            | Get a staff member                           |
| PUT    | `/staff/{id}`            | Update a staff member                        |
| DELETE | `/staff/{id}`            | Delete a staff member                        |

## Running Tests

```bash
cd backend
pytest
```

Tests run against an in-memory SQLite database, so PostgreSQL does not need to be running.

## Author

[@hammad-cloud](https://github.com/hammad-cloud)
