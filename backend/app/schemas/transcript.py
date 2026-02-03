"""
Pydantic schemas for Transcript API
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class TranscriptResponse(BaseModel):
    """Response schema for transcript"""
    id: UUID
    call_id: UUID
    speaker: str
    text: str
    timestamp: datetime
    confidence: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


class TranscriptListResponse(BaseModel):
    """Response schema for list of transcripts"""
    call_id: UUID
    transcripts: list[TranscriptResponse]
