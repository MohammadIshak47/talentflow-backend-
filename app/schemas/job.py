from datetime import datetime

from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    title: str
    slug: str
    company_id: str
    department: str
    status: str
    salary_min: int
    salary_max: int
    experience_level: str
    type: str
    remote: bool
    description: str
    skills: list[str]
    created_at: datetime
    applications_count: int

    class Config:
        from_attributes = True


class CreateJobRequest(BaseModel):
    title: str
    department: str
    salary_min: int
    salary_max: int
    experience_level: str
    type: str
    remote: bool
    description: str
    skills: list[str] = []
    status: str = "draft"


class UpdateJobRequest(BaseModel):
    title: str | None = None
    department: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    experience_level: str | None = None
    type: str | None = None
    remote: bool | None = None
    description: str | None = None
    skills: list[str] | None = None
    status: str | None = None


class StageOut(BaseModel):
    id: str
    company_id: str
    name: str
    color: str
    order: int

    class Config:
        from_attributes = True


class CreateStageRequest(BaseModel):
    company_id: str
    name: str
    color: str = "#6366f1"
    order: int = 0


class UpdateStageRequest(BaseModel):
    name: str | None = None
    color: str | None = None
    order: int | None = None


class ReorderStagesRequest(BaseModel):
    order: list[str]
