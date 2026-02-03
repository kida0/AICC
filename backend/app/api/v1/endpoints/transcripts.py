"""
Transcript API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.call import Call
from app.models.transcript import Transcript
from app.schemas.transcript import TranscriptListResponse, TranscriptResponse

router = APIRouter(prefix="/transcripts", tags=["transcripts"])
logger = logging.getLogger(__name__)


@router.get("/{call_id}", response_model=TranscriptListResponse)
async def get_call_transcripts(call_id: str, db: Session = Depends(get_db)):
    """
    Get all transcripts for a call

    Args:
        call_id: Call ID
        db: Database session

    Returns:
        TranscriptListResponse: List of transcripts

    Raises:
        HTTPException: If call not found
    """
    # Check if call exists
    call = db.query(Call).filter(Call.id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Get transcripts
    transcripts = (
        db.query(Transcript)
        .filter(Transcript.call_id == call_id)
        .order_by(Transcript.timestamp)
        .all()
    )

    return TranscriptListResponse(
        call_id=call_id,
        transcripts=transcripts
    )
