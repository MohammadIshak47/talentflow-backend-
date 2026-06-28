from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import Application
from app.models.user import User
from app.schemas.application import ApplicationOut, CandidateBasic, MoveStageRequest, RejectRequest
from app.schemas.common import ok, paginated

router = APIRouter(prefix="/applications", tags=["applications"])


def _to_out(app: Application) -> ApplicationOut:
    return ApplicationOut(
        id=app.id,
        job_id=app.job_id,
        candidate_id=app.candidate_id,
        stage_id=app.stage_id,
        status=app.status,
        applied_at=app.applied_at,
        score=app.score,
        candidate=CandidateBasic(
            name=app.candidate.name,
            email=app.candidate.email,
            avatar=app.candidate.avatar,
        ),
    )


@router.get("")
def list_applications(job_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Application).options(joinedload(Application.candidate))
    if job_id:
        query = query.filter(Application.job_id == job_id)
    applications = query.order_by(Application.applied_at.desc()).all()
    items = [_to_out(a) for a in applications]
    return paginated(items, len(items), 1, max(len(items), 1))


@router.get("/{application_id}")
def get_application(application_id: str, db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return ok(_to_out(app))


@router.patch("/{application_id}/stage")
def move_stage(application_id: str, payload: MoveStageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.stage_id = payload.stage_id
    db.commit()
    db.refresh(app)
    return ok(_to_out(app))


@router.patch("/{application_id}/reject")
def reject(application_id: str, payload: RejectRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "rejected"
    app.rejection_reason = payload.reason
    db.commit()
    db.refresh(app)
    return ok(_to_out(app))


@router.patch("/{application_id}/hire")
def hire(application_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "hired"
    db.commit()
    db.refresh(app)
    return ok(_to_out(app))


@router.patch("/{application_id}/withdraw")
def withdraw(application_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "withdrawn"
    db.commit()
    db.refresh(app)
    return ok(_to_out(app))
