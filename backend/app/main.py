"""Application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Run startup and shutdown tasks for the application."""
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "CRUD API for managing patient records. "
        "Patient endpoints require a JWT obtained from /api/v1/auth/login."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"message": f"{settings.app_name} is running"}


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return API health status."""
    return {"status": "ok"}
