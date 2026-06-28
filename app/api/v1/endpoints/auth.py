from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.candidate import CandidateProfile
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UpdateMeRequest, UserOut
from app.schemas.common import ok

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
        role=payload.role,
    )
    db.add(user)
    db.flush()

    # Candidates get a profile row created right away so /candidates/me always works.
    if user.role == "candidate":
        db.add(CandidateProfile(user_id=user.id))

    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    return ok(AuthResponse(user=UserOut.model_validate(user), token=token))


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=user.id)
    return ok(AuthResponse(user=UserOut.model_validate(user), token=token))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # JWTs are stateless; logout is handled client-side by discarding the token.
    return ok(None)


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(current_user))


@router.patch("/me")
def update_me(payload: UpdateMeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return ok(UserOut.model_validate(current_user))
