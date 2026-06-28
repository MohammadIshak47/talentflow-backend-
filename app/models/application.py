from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import UUIDPkMixin


class Application(UUIDPkMixin, Base):
    __tablename__ = "applications"

    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    stage_id: Mapped[str | None] = mapped_column(ForeignKey("stages.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")  # active|hired|rejected|withdrawn
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    score: Mapped[float] = mapped_column(Float, default=0)
    cover_letter: Mapped[str | None] = mapped_column(String, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    job: Mapped["Job"] = relationship(back_populates="applications")
    candidate: Mapped["User"] = relationship()
    stage: Mapped["Stage"] = relationship(back_populates="applications")
    interviews: Mapped[list["Interview"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class Interview(UUIDPkMixin, Base):
    __tablename__ = "interviews"

    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    interviewer: Mapped[str] = mapped_column(String, default="")
    type: Mapped[str] = mapped_column(String, default="video")
    link: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="scheduled")  # scheduled|completed|cancelled|no_show
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    application: Mapped["Application"] = relationship(back_populates="interviews")
