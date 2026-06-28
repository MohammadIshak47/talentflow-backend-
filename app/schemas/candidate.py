from pydantic import BaseModel


class EducationOut(BaseModel):
    id: str
    institution: str
    degree: str
    field: str
    start_year: int
    end_year: int
    gpa: str | None = None

    class Config:
        from_attributes = True


class EducationIn(BaseModel):
    institution: str
    degree: str = ""
    field: str = ""
    start_year: int
    end_year: int
    gpa: str | None = None


class ExperienceOut(BaseModel):
    id: str
    company: str
    title: str
    start: str
    end: str
    description: str

    class Config:
        from_attributes = True


class ExperienceIn(BaseModel):
    company: str
    title: str
    start: str = ""
    end: str = ""
    description: str = ""


class LanguageOut(BaseModel):
    id: str
    language: str
    proficiency: str

    class Config:
        from_attributes = True


class CertificationOut(BaseModel):
    id: str
    name: str
    issuer: str
    year: int

    class Config:
        from_attributes = True


class CandidateProfileOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str | None = None
    headline: str | None = None
    location: str | None = None
    bio: str | None = None
    status: str
    desired_salary_min: int | None = None
    desired_salary_max: int | None = None
    educations: list[EducationOut] = []
    experiences: list[ExperienceOut] = []
    skills: list[str] = []
    languages: list[LanguageOut] = []
    certifications: list[CertificationOut] = []
    resume_score: float = 0

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    phone: str | None = None
    headline: str | None = None
    location: str | None = None
    bio: str | None = None
    status: str | None = None
    desired_salary_min: int | None = None
    desired_salary_max: int | None = None
    skills: list[str] | None = None


class JobAlertOut(BaseModel):
    id: str
    keywords: str
    location: str
    frequency: str

    class Config:
        from_attributes = True


class JobAlertIn(BaseModel):
    keywords: str
    location: str = ""
    frequency: str = "weekly"


class SaveJobRequest(BaseModel):
    job_id: str
