"""Async job endpoints backed by the Redis queue (JWT protected)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from app.api.deps import get_current_admin
from app.core.cache import get_redis
from app.jobs import patient_report
from app.models.user import User

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _redis():  # type: ignore[no-untyped-def]
    connection = get_redis()
    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job queue is not configured.",
        )
    return connection


@router.post(
    "/patient-report",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue a patient report job",
)
def queue_patient_report(_: Annotated[User, Depends(get_current_admin)]) -> dict[str, str]:
    """Enqueue the report and return immediately with its job ID."""
    job = Queue(connection=_redis()).enqueue(patient_report)
    return {"job_id": job.id}


@router.get("/{job_id}", summary="Get job status and result")
def get_job(job_id: str, _: Annotated[User, Depends(get_current_admin)]) -> dict:
    """Return the job status, plus its result once finished."""
    try:
        job = Job.fetch(job_id, connection=_redis())
    except NoSuchJobError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} was not found.",
        ) from exc
    return {"id": job.id, "status": job.get_status().value, "result": job.return_value()}
