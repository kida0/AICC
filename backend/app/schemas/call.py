"""
Pydantic schemas for Call API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CallInitiate(BaseModel):
    """Request schema for initiating a call"""
    phone_number: str = Field(..., description="Destination phone number in E.164 format")
    caller_id: Optional[str] = Field(None, description="Optional caller ID")
    ai_persona: Optional[str] = Field("customer_support", description="AI persona to use")


class CallResponse(BaseModel):
    """Response schema for call"""
    id: UUID
    phone_number: str
    status: str
    caller_id: Optional[str]
    direction: str
    twilio_call_sid: Optional[str]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration: Optional[int]
    recording_url: Optional[str]
    ai_persona: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallListResponse(BaseModel):
    """Response schema for list of calls with pagination"""
    items: list[CallResponse]
    total: int
    page: int
    page_size: int
    pages: int


class CallInitiateResponse(BaseModel):
    """Response schema for call initiation"""
    call_id: UUID
    status: str
    phone_number: str
    created_at: datetime
    websocket_url: str
