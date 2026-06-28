import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import Application
from app.models.candidate import CandidateProfile, Education, Experience, JobAlert, SavedJob
from app.models.job import Job
from app.models.user import User
from app.schemas.application import ApplyRequest, CandidateBasic
from app.schemas.candidate import (
    CandidateProfileOut,
    EducationIn,
    ExperienceIn,
    JobAlertIn,
    SaveJobRequest,
    UpdateProfileRequest,
)
from app.schemas.common import ok, paginated

router = APIRouter(tags=["candidates"])


def _profile_out(profile: CandidateProfile) -> CandidateProfileOut:
    return CandidateProfileOut(
        id=profile.id,
        name=profile.user.name,
        email=profile.user.email,
        phone=profile.phone,
        headline=profile.headline,
        location=profile.location,
        bio=profile.bio,
        status=profile.status,
        desired_salary_min=profile.desired_salary_min,
        desired_salary_max=profile.desired_salary_max,
        educations=profile.educations,
        experiences=profile.experiences,
        skills=profile.skills or [],
        languages=profile.languages,
        certifications=profile.certifications,
        resume_score=profile.resume_score,
    )


def _get_or_create_profile(db: Session, user: User) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/candidates/me")
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db, current_user)
    return ok(_profile_out(profile))


@router.patch("/candidates/me")
def update_my_profile(payload: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return ok(_profile_out(profile))


@router.post("/candidates/me/experiences")
def add_experience(payload: ExperienceIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db, current_user)
    experience = Experience(profile_id=profile.id, **payload.model_dump())
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return ok(experience)


@router.patch("/candidates/me/experiences/{experience_id}")
def update_experience(experience_id: str, payload: ExperienceIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experience = db.get(Experience, experience_id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(experience, field, value)
    db.commit()
    db.refresh(experience)
    return ok(experience)


@router.delete("/candidates/me/experiences/{experience_id}")
def delete_experience(experience_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experience = db.get(Experience, experience_id)
    if experience:
        db.delete(experience)
        db.commit()
    return ok(None)


@router.post("/candidates/me/educations")
def add_education(payload: EducationIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db, current_user)
    education = Education(profile_id=profile.id, **payload.model_dump())
    db.add(education)
    db.commit()
    db.refresh(education)
    return ok(education)


@router.patch("/candidates/me/educations/{education_id}")
def update_education(education_id: str, payload: EducationIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    education = db.get(Education, education_id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(education, field, value)
    db.commit()
    db.refresh(education)
    return ok(education)


@router.delete("/candidates/me/educations/{education_id}")
def delete_education(education_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    education = db.get(Education, education_id)
    if education:
        db.delete(education)
        db.commit()
    return ok(None)


@router.post("/candidates/me/resume")
def upload_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # NOTE: free-tier hosts (Render/Vercel/Railway) have ephemeral filesystems,
    # so this stores files under /tmp for the demo. For production, swap this
    # for an upload to S3 / Cloudinary / Supabase Storage and save the returned URL.
    profile = _get_or_create_profile(db, current_user)
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    path = f"/tmp/{filename}"
    with open(path, "wb") as f:
        f.write(file.file.read())

    # Placeholder scoring logic — replace with real resume-parsing/scoring later.
    score = 75.0
    profile.resume_url = path
    profile.resume_score = score
    db.commit()

    return {"url": path, "score": score}


@router.get("/job-alerts")
def list_job_alerts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alerts = db.query(JobAlert).filter(JobAlert.user_id == current_user.id).all()
    return ok(alerts)


@router.post("/job-alerts")
def create_job_alert(payload: JobAlertIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = JobAlert(user_id=current_user.id, **payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return ok(alert)


@router.delete("/job-alerts/{alert_id}")
def delete_job_alert(alert_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = db.get(JobAlert, alert_id)
    if alert and alert.user_id == current_user.id:
        db.delete(alert)
        db.commit()
    return ok(None)


@router.get("/saved-jobs")
def list_saved_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).all()
    return ok([s.job_id for s in saved])


@router.post("/saved-jobs")
def save_job(payload: SaveJobRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exists = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == payload.job_id).first()
    if not exists:
        db.add(SavedJob(user_id=current_user.id, job_id=payload.job_id))
        db.commit()
    return ok(None)


@router.delete("/saved-jobs/{job_id}")
def unsave_job(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id).first()
    if saved:
        db.delete(saved)
        db.commit()
    return ok(None)


@router.get("/candidates/me/applications")
def list_my_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = (
        db.query(Application)
        .options(joinedload(Application.candidate))
        .filter(Application.candidate_id == current_user.id)
        .all()
    )
    items = [
        {
            "id": a.id,
            "job_id": a.job_id,
            "candidate_id": a.candidate_id,
            "stage_id": a.stage_id,
            "status": a.status,
            "applied_at": a.applied_at,
            "score": a.score,
            "candidate": CandidateBasic(name=a.candidate.name, email=a.candidate.email, avatar=a.candidate.avatar),
        }
        for a in applications
    ]
    return paginated(items, len(items), 1, max(len(items), 1))


@router.post("/candidates/apply")
def apply_to_job(payload: ApplyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = (
        db.query(Application)
        .filter(Application.job_id == payload.job_id, Application.candidate_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You already applied to this job")

    application = Application(
        job_id=payload.job_id,
        candidate_id=current_user.id,
        cover_letter=payload.cover_letter,
        status="active",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return ok({
        "id": application.id,
        "job_id": application.job_id,
        "candidate_id": application.candidate_id,
        "stage_id": application.stage_id,
        "status": application.status,
        "applied_at": application.applied_at,
        "score": application.score,
        "candidate": CandidateBasic(name=current_user.name, email=current_user.email, avatar=current_user.avatar),
    })
