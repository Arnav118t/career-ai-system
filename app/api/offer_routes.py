from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import schemas
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/offers")
def add_offer(
    offer: schemas.OfferCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_offer = models.Offer(
        user_id=current_user.id,
        **offer.dict()
    )

    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    return new_offer