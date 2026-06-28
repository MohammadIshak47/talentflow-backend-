import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_recruiter
from app.db.session import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.common import paginated, ok
from app.schemas.job import CreateJobRequest, JobOut, UpdateJobRequest

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{slug}-{uuid.uuid4().hex[:6]}"


@router.get("")
def list_jobs(
    search: str | None = None,
    remote: bool | None = None,
    level: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    if remote is not None:
        query = query.filter(Job.remote == remote)
    if level:
        query = query.filter(Job.experience_level == level)
    if status:
        query = query.filter(Job.status == status)

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    items = [JobOut.model_validate(j) for j in jobs]
    return paginated(items, total, page, per_page)


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return ok(JobOut.model_validate(job))


@router.post("")
def create_job(
    payload: CreateJobRequest,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User has no associated company")

    job = Job(
        **payload.model_dump(),
        company_id=current_user.company_id,
        slug=_slugify(payload.title),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return ok(JobOut.model_validate(job))


@router.patch("/{job_id}")
def update_job(
    job_id: str,
    payload: UpdateJobRequest,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    job = _get_owned_job(db, job_id, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return ok(JobOut.model_validate(job))


@router.delete("/{job_id}")
def delete_job(job_id: str, current_user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    job = _get_owned_job(db, job_id, current_user)
    db.delete(job)
    db.commit()
    return ok(None)


@router.patch("/{job_id}/publish")
def publish_job(job_id: str, current_user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    job = _get_owned_job(db, job_id, current_user)
    job.status = "published"
    db.commit()
    db.refresh(job)
    return ok(JobOut.model_validate(job))


@router.patch("/{job_id}/pause")
def pause_job(job_id: str, current_user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    job = _get_owned_job(db, job_id, current_user)
    job.status = "paused"
    db.commit()
    db.refresh(job)
    return ok(JobOut.model_validate(job))


def _get_owned_job(db: Session, job_id: str, current_user: User) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not your company's job")
    return job
