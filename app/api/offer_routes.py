from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import schemas
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/offers", response_model=List[schemas.OfferResponse])
def list_offers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(models.Offer)
        .filter(models.Offer.user_id == current_user.id)
        .order_by(models.Offer.id.desc())
        .all()
    )


@router.post("/offers", response_model=schemas.OfferResponse, status_code=201)
def add_offer(
    offer: schemas.OfferCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_offer = models.Offer(
        user_id=current_user.id,
        **offer.model_dump()
    )

    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    return new_offer