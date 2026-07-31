"""Aggregates all v1 endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, doctors

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(doctors.router)
