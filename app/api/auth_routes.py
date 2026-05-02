from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import schemas
from app.services import auth_service

router = APIRouter()

# ==================== REGISTER ====================

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    return auth_service.create_user(db, user)


# ==================== LOGIN ====================

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login and get JWT token
    """
    return auth_service.authenticate_user(db, user)


# ==================== CURRENT USER ====================

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_profile(
    current_user = Depends(auth_service.get_current_user)
):
    """
    Get currently logged-in user
    """
    return current_user