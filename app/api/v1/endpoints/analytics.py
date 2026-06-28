from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import Application
from app.models.job import Job, Stage
from app.models.user import User
from app.schemas.common import ok

router = APIRouter(prefix="/analytics", tags=["analytics"])

STAGE_COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#3b82f6"]


def _funnel(db: Session, job_id: str | None = None) -> list[dict]:
    query = db.query(Application).join(Stage, Application.stage_id == Stage.id)
    if job_id:
        query = query.filter(Application.job_id == job_id)

    counts = Counter(stage_name for (stage_name,) in query.with_entities(Stage.name))
    return [
        {"stage": name, "count": count, "color": STAGE_COLORS[i % len(STAGE_COLORS)]}
        for i, (name, count) in enumerate(counts.items())
    ]


def _over_time(db: Session) -> list[dict]:
    rows = (
        db.query(func.to_char(Application.applied_at, "Mon"), func.count(Application.id))
        .group_by(func.to_char(Application.applied_at, "Mon"), func.extract("month", Application.applied_at))
        .order_by(func.extract("month", Application.applied_at))
        .all()
    )
    return [{"month": month, "apps": count} for month, count in rows]


def _time_to_hire(db: Session) -> float:
    hired = db.query(Application).filter(Application.status == "hired").all()
    if not hired:
        return 0.0
    days = [(datetime.utcnow() - a.applied_at.replace(tzinfo=None)).days for a in hired]
    return round(sum(days) / len(days), 1)


def _offer_acceptance(db: Session) -> float:
    hired = db.query(Application).filter(Application.status == "hired").count()
    total_closed = db.query(Application).filter(Application.status.in_(["hired", "rejected", "withdrawn"])).count()
    return round((hired / total_closed) * 100, 1) if total_closed else 0.0


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    active_jobs = db.query(Job).filter(Job.status == "published").count()
    total_candidates = db.query(User).filter(User.role == "candidate").count()
    data = {
        "funnel": _funnel(db),
        "over_time": _over_time(db),
        "time_to_hire": _time_to_hire(db),
        "offer_acceptance": _offer_acceptance(db),
        "active_jobs": active_jobs,
        "total_candidates": total_candidates,
    }
    return ok(data)


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    active_jobs = db.query(Job).filter(Job.status == "published").count()
    total_candidates = db.query(User).filter(User.role == "candidate").count()
    return ok({
        "active_jobs": active_jobs,
        "total_candidates": total_candidates,
        "time_to_hire": _time_to_hire(db),
        "offer_acceptance": _offer_acceptance(db),
    })


@router.get("/funnel")
def get_funnel(job_id: str | None = None, db: Session = Depends(get_db)):
    return ok(_funnel(db, job_id))


@router.get("/applications-over-time")
def get_applications_over_time(db: Session = Depends(get_db)):
    return ok(_over_time(db))
