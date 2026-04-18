from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import schemas
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/profile")
def create_profile(
    profile: schemas.ProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    new_profile = models.Profile(
        user_id=current_user.id,
        **profile.dict()
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile