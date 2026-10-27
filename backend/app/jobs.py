"""Background jobs executed by the RQ worker (`rq worker`)."""

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.patient import Patient


def patient_report() -> dict:
    """Count patients per status; runs in the worker, not the API process."""
    db = SessionLocal()
    try:
        rows = db.execute(select(Patient.status, func.count()).group_by(Patient.status)).all()
    finally:
        db.close()
    by_status = {status: count for status, count in rows}
    return {"total": sum(by_status.values()), "by_status": by_status}
