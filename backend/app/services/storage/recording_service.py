"""
Recording service - handles call recording management
"""
import logging
import io
import wave
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.call import Call
from app.services.storage.local_storage_service import local_storage_service
from app.core.exceptions import StorageException

logger = logging.getLogger(__name__)


class RecordingService:
    """Service for managing call recordings"""

    def __init__(self):
        self.storage = local_storage_service

    async def save_call_recording(
        self,
        call_id: str,
        audio_chunks: list,
        sample_rate: int = 8000,
        db: Optional[Session] = None
    ) -> str:
        """
        Save call recording as WAV file

        Args:
            call_id: Call ID
            audio_chunks: List of PCM audio chunks
            sample_rate: Sample rate (default 8000 Hz)
            db: Database session

        Returns:
            str: File path

        Raises:
            StorageException: If save fails
        """
        try:
            # Combine all audio chunks
            combined_audio = b''.join(audio_chunks)

            # Create WAV file
            wav_data = self._create_wav_file(combined_audio, sample_rate)

            # Save to local storage
            filepath = self.storage.save_recording(
                call_id=call_id,
                audio_data=wav_data,
                file_format="wav"
            )

            # Update database if session provided
            if db:
                call = db.query(Call).filter(Call.id == call_id).first()
                if call:
                    call.recording_s3_key = filepath  # Using same field for local path
                    call.recording_url = self.storage.get_recording_url(call_id)
                    db.commit()

            logger.info(f"Call recording saved: {filepath}")

            return filepath

        except Exception as e:
            logger.error(f"Failed to save call recording: {e}")
            raise StorageException(f"Failed to save recording: {e}")

    def _create_wav_file(
        self,
        pcm_data: bytes,
        sample_rate: int = 8000,
        channels: int = 1
    ) -> bytes:
        """
        Create WAV file from PCM data

        Args:
            pcm_data: PCM audio bytes (16-bit)
            sample_rate: Sample rate
            channels: Number of channels

        Returns:
            bytes: WAV file data
        """
        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)

        wav_data = wav_buffer.getvalue()
        return wav_data

    async def get_recording(self, call_id: str) -> Optional[str]:
        """
        Get recording file path

        Args:
            call_id: Call ID

        Returns:
            str: File path or None
        """
        return self.storage.get_recording_path(call_id)


# Global recording service instance
recording_service = RecordingService()
