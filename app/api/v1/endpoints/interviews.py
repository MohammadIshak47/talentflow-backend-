from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import Interview
from app.models.user import User
from app.schemas.application import (
    CompleteInterviewRequest,
    InterviewOut,
    ScheduleInterviewRequest,
    UpdateInterviewRequest,
)
from app.schemas.common import ok, paginated

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.get("")
def list_interviews(db: Session = Depends(get_db)):
    interviews = db.query(Interview).order_by(Interview.scheduled_at).all()
    items = [InterviewOut.model_validate(i) for i in interviews]
    return paginated(items, len(items), 1, max(len(items), 1))


@router.get("/{interview_id}")
def get_interview(interview_id: str, db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return ok(InterviewOut.model_validate(interview))


@router.post("")
def schedule_interview(payload: ScheduleInterviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = Interview(**payload.model_dump())
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return ok(InterviewOut.model_validate(interview))


@router.patch("/{interview_id}")
def update_interview(interview_id: str, payload: UpdateInterviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interview, field, value)
    db.commit()
    db.refresh(interview)
    return ok(InterviewOut.model_validate(interview))


@router.patch("/{interview_id}/cancel")
def cancel_interview(interview_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    interview.status = "cancelled"
    db.commit()
    db.refresh(interview)
    return ok(InterviewOut.model_validate(interview))


@router.patch("/{interview_id}/complete")
def complete_interview(interview_id: str, payload: CompleteInterviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    interview.status = "completed"
    interview.notes = payload.notes
    db.commit()
    db.refresh(interview)
    return ok(InterviewOut.model_validate(interview))
