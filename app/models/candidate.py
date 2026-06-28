from sqlalchemy import ARRAY, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import UUIDPkMixin


class CandidateProfile(UUIDPkMixin, Base):
    __tablename__ = "candidate_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    headline: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="open")  # actively_looking|open|not_looking
    desired_salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    desired_salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    resume_url: Mapped[str | None] = mapped_column(String, nullable=True)
    resume_score: Mapped[float] = mapped_column(Float, default=0)

    user: Mapped["User"] = relationship(back_populates="candidate_profile")
    educations: Mapped[list["Education"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    experiences: Mapped[list["Experience"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    languages: Mapped[list["Language"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    certifications: Mapped[list["Certification"]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class Education(UUIDPkMixin, Base):
    __tablename__ = "educations"

    profile_id: Mapped[str] = mapped_column(ForeignKey("candidate_profiles.id"), nullable=False)
    institution: Mapped[str] = mapped_column(String, nullable=False)
    degree: Mapped[str] = mapped_column(String, default="")
    field: Mapped[str] = mapped_column(String, default="")
    start_year: Mapped[int] = mapped_column(Integer, default=0)
    end_year: Mapped[int] = mapped_column(Integer, default=0)
    gpa: Mapped[str | None] = mapped_column(String, nullable=True)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="educations")


class Experience(UUIDPkMixin, Base):
    __tablename__ = "experiences"

    profile_id: Mapped[str] = mapped_column(ForeignKey("candidate_profiles.id"), nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    start: Mapped[str] = mapped_column(String, default="")
    end: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(String, default="")

    profile: Mapped["CandidateProfile"] = relationship(back_populates="experiences")


class Language(UUIDPkMixin, Base):
    __tablename__ = "languages"

    profile_id: Mapped[str] = mapped_column(ForeignKey("candidate_profiles.id"), nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    proficiency: Mapped[str] = mapped_column(String, default="")

    profile: Mapped["CandidateProfile"] = relationship(back_populates="languages")


class Certification(UUIDPkMixin, Base):
    __tablename__ = "certifications"

    profile_id: Mapped[str] = mapped_column(ForeignKey("candidate_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    issuer: Mapped[str] = mapped_column(String, default="")
    year: Mapped[int] = mapped_column(Integer, default=0)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="certifications")


class JobAlert(UUIDPkMixin, Base):
    __tablename__ = "job_alerts"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    keywords: Mapped[str] = mapped_column(String, default="")
    location: Mapped[str] = mapped_column(String, default="")
    frequency: Mapped[str] = mapped_column(String, default="weekly")  # daily|weekly


class SavedJob(UUIDPkMixin, Base):
    __tablename__ = "saved_jobs"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
