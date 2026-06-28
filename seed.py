"""
Seeds the database with a demo company, recruiter, candidate, jobs, stages,
and one application — enough to click through the whole frontend immediately
after deploying.

Usage:
    python seed.py
"""

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.candidate import CandidateProfile
from app.models.job import Job, Stage
from app.models.user import Company, User
from app.models.application import Application
import app.models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Company).first():
            print("Database already has data — skipping seed.")
            return

        company = Company(
            name="Acme Inc.",
            slug="acme-inc",
            industry="Software",
            description="A demo company for TalentFlow.",
            size="11-50",
            website="https://acme.example.com",
            plan="free",
        )
        db.add(company)
        db.flush()

        admin = User(
            email="admin@acme.com",
            hashed_password=hash_password("password123"),
            name="Amir Admin",
            role="company_admin",
            company_id=company.id,
        )
        recruiter = User(
            email="recruiter@acme.com",
            hashed_password=hash_password("password123"),
            name="Riya Recruiter",
            role="recruiter",
            company_id=company.id,
        )
        candidate = User(
            email="candidate@gmail.com",
            hashed_password=hash_password("password123"),
            name="Alex Candidate",
            role="candidate",
        )
        db.add_all([admin, recruiter, candidate])
        db.flush()

        db.add(CandidateProfile(
            user_id=candidate.id,
            headline="Full-Stack Developer",
            location="Dhaka, BD",
            status="actively_looking",
            skills=["Python", "FastAPI", "React"],
        ))

        stages = [
            Stage(company_id=company.id, name="Applied", color="#6366f1", order=0),
            Stage(company_id=company.id, name="Screening", color="#8b5cf6", order=1),
            Stage(company_id=company.id, name="Interview", color="#ec4899", order=2),
            Stage(company_id=company.id, name="Offer", color="#10b981", order=3),
        ]
        db.add_all(stages)
        db.flush()

        job = Job(
            title="Backend Engineer (FastAPI)",
            slug="backend-engineer-fastapi",
            company_id=company.id,
            department="Engineering",
            status="published",
            salary_min=60000,
            salary_max=90000,
            experience_level="mid",
            type="full_time",
            remote=True,
            description="Build and maintain our FastAPI services.",
            skills=["Python", "FastAPI", "PostgreSQL"],
        )
        db.add(job)
        db.flush()

        db.add(Application(
            job_id=job.id,
            candidate_id=candidate.id,
            stage_id=stages[0].id,
            status="active",
            score=82,
        ))

        db.commit()
        print("Seed complete.")
        print("Admin login: admin@acme.com / password123")
        print("Recruiter login: recruiter@acme.com / password123")
        print("Candidate login: candidate@gmail.com / password123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
