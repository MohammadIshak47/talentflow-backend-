from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    company_id: str | None
    avatar: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "candidate"  # candidate | recruiter


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: UserOut
    token: str


class UpdateMeRequest(BaseModel):
    name: str | None = None
    avatar: str | None = None
