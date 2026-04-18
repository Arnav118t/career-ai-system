from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.decision_service import generate_recommendations
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/recommend")
def recommend_jobs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return generate_recommendations(db, current_user.id)