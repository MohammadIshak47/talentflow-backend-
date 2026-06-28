from datetime import datetime

from pydantic import BaseModel


class CandidateBasic(BaseModel):
    name: str
    email: str
    avatar: str | None = None


class ApplicationOut(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    stage_id: str | None
    status: str
    applied_at: datetime
    score: float
    candidate: CandidateBasic

    class Config:
        from_attributes = True


class MoveStageRequest(BaseModel):
    stage_id: str


class RejectRequest(BaseModel):
    reason: str | None = None


class ApplyRequest(BaseModel):
    job_id: str
    cover_letter: str | None = None
    resume_id: str | None = None


class InterviewOut(BaseModel):
    id: str
    application_id: str
    scheduled_at: datetime
    interviewer: str
    type: str
    link: str
    status: str

    class Config:
        from_attributes = True


class ScheduleInterviewRequest(BaseModel):
    application_id: str
    scheduled_at: datetime
    interviewer: str
    type: str
    link: str


class UpdateInterviewRequest(BaseModel):
    scheduled_at: datetime | None = None
    interviewer: str | None = None
    type: str | None = None
    link: str | None = None


class CompleteInterviewRequest(BaseModel):
    notes: str | None = None
