from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import get_current_user
from app.services.resume_service import process_resume

router = APIRouter()


@router.post("/resume/upload")
@router.post("/upload-resume", include_in_schema=False)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await process_resume(db, current_user.id, file)
