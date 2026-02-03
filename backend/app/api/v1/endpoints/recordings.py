"""
Recording API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import logging

from app.core.database import get_db
from app.models.call import Call
from app.services.storage.local_storage_service import local_storage_service

router = APIRouter(prefix="/recordings", tags=["recordings"])
logger = logging.getLogger(__name__)


@router.get("/{call_id}")
async def get_recording(call_id: str, db: Session = Depends(get_db)):
    """
    Get call recording audio file

    Args:
        call_id: Call ID
        db: Database session

    Returns:
        FileResponse: Audio file

    Raises:
        HTTPException: If recording not found
    """
    # Check if call exists
    call = db.query(Call).filter(Call.id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Get recording file path
    filepath = local_storage_service.get_recording_path(call_id)

    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Recording not found")

    # Return audio file
    return FileResponse(
        path=filepath,
        media_type="audio/wav",
        filename=f"call_{call_id}.wav"
    )
