from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import schemas
from app.services.auth_service import get_current_user, create_or_update_profile

router = APIRouter()


@router.get("/profile", response_model=schemas.ProfileResponse)
def read_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = (
        db.query(models.Profile)
        .filter(models.Profile.user_id == current_user.id)
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.post("/profile", response_model=schemas.ProfileResponse)
def create_profile(
    profile: schemas.ProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_or_update_profile(db, current_user.id, profile)
