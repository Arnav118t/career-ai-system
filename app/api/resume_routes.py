from fastapi import APIRouter, UploadFile, File
from app.services.resume_service import parse_resume
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    text = await parse_resume(file)

    return {
        "resume_text": text
    }