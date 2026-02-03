"""
Transcript database model
"""
from sqlalchemy import Column, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Transcript(Base):
    """
    Transcript model representing conversation turns

    Attributes:
        id: Unique identifier
        call_id: Foreign key to Call
        speaker: Speaker type ('user' or 'ai')
        text: Transcript text
        timestamp: When this was spoken
        confidence: STT confidence score (0.0-1.0)
        audio_segment_s3_key: Optional S3 key for individual turn audio
        created_at: Record creation timestamp
    """

    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker = Column(String(10), nullable=False)  # 'user' or 'ai'
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    confidence = Column(Numeric(3, 2), nullable=True)
    audio_segment_s3_key = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    call = relationship("Call", back_populates="transcripts")

    def __repr__(self):
        return f"<Transcript(id={self.id}, speaker={self.speaker}, call_id={self.call_id})>"
