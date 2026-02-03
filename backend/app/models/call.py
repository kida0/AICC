"""
Call database model
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Call(Base):
    """
    Call model representing a phone call session

    Attributes:
        id: Unique identifier
        phone_number: Destination phone number
        caller_id: Caller ID (Twilio phone number)
        status: Call status (initiating, ringing, in_progress, completed, failed)
        direction: Call direction (outbound)
        twilio_call_sid: Twilio call SID
        started_at: Call start timestamp
        ended_at: Call end timestamp
        duration: Call duration in seconds
        recording_s3_key: S3 key for recording file
        recording_url: Presigned URL for recording playback
        ai_persona: AI persona used for the call
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """

    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), nullable=False, index=True)
    caller_id = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), default="outbound")
    twilio_call_sid = Column(String(100), unique=True, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)

    recording_s3_key = Column(String(500), nullable=True)
    recording_url = Column(Text, nullable=True)

    ai_persona = Column(String(50), default="customer_support")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    transcripts = relationship("Transcript", back_populates="call", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Call(id={self.id}, phone_number={self.phone_number}, status={self.status})>"
