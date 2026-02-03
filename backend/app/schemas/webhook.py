"""
Pydantic schemas for Twilio webhooks
"""
from pydantic import BaseModel
from typing import Optional


class TwilioCallStatus(BaseModel):
    """Twilio call status webhook schema"""
    CallSid: str
    AccountSid: str
    From: str
    To: str
    CallStatus: str
    Duration: Optional[str] = None
    RecordingUrl: Optional[str] = None


class TwilioVoiceRequest(BaseModel):
    """Twilio voice webhook schema"""
    CallSid: str
    AccountSid: str
    From: str
    To: str
    CallStatus: str
