from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_recruiter
from app.db.session import get_db
from app.models.job import Stage
from app.models.user import User
from app.schemas.common import ok
from app.schemas.job import CreateStageRequest, ReorderStagesRequest, StageOut, UpdateStageRequest

router = APIRouter(prefix="/stages", tags=["stages"])


@router.get("")
def list_stages(company_id: str, db: Session = Depends(get_db)):
    stages = db.query(Stage).filter(Stage.company_id == company_id).order_by(Stage.order).all()
    return ok([StageOut.model_validate(s) for s in stages])


@router.post("")
def create_stage(payload: CreateStageRequest, current_user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    stage = Stage(**payload.model_dump())
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return ok(StageOut.model_validate(stage))


@router.patch("/reorder")
def reorder_stages(payload: ReorderStagesRequest, current_user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    stages = []
    for index, stage_id in enumerate(payload.order):
        stage = db.get(Stage, stage_id)
        if stage:
            stage.order = index
            stages.append(stage)
    db.commit()
    return ok([StageOut.model_validate(s) for s in sorted(stages, key=lambda s: s.order)])


@router.patch("/{stage_id}")
def update_stage(stage_id: str, payload: UpdateStageRequest, current_user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(stage, field, value)
    db.commit()
    db.refresh(stage)
    return ok(StageOut.model_validate(stage))


@router.delete("/{stage_id}")
def delete_stage(stage_id: str, current_user: User = Depends(require_recruiter), db: Session = Depends(get_db)):
    stage = db.get(Stage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    db.delete(stage)
    db.commit()
    return ok(None)
