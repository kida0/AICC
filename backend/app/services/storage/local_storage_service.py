"""
Local file storage service (simplified for testing)
"""
import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import shutil

from app.config.settings import settings
from app.core.exceptions import StorageException

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Local file storage service"""

    def __init__(self):
        """Initialize local storage"""
        # Create recordings directory
        self.recordings_dir = Path("recordings")
        self.recordings_dir.mkdir(exist_ok=True)
        logger.info(f"Local storage initialized: {self.recordings_dir.absolute()}")

    def save_recording(
        self,
        call_id: str,
        audio_data: bytes,
        file_format: str = "wav"
    ) -> str:
        """
        Save call recording to local directory

        Args:
            call_id: Call ID
            audio_data: Audio data bytes
            file_format: File format (wav, mp3, etc.)

        Returns:
            str: File path

        Raises:
            StorageException: If save fails
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{call_id}_{timestamp}.{file_format}"
            filepath = self.recordings_dir / filename

            # Write audio data
            with open(filepath, "wb") as f:
                f.write(audio_data)

            logger.info(f"Recording saved: {filepath}")

            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            raise StorageException(f"Failed to save recording: {e}")

    def get_recording_path(self, call_id: str) -> Optional[str]:
        """
        Get recording file path for a call

        Args:
            call_id: Call ID

        Returns:
            str: File path or None if not found
        """
        try:
            # Find file matching call_id
            for filepath in self.recordings_dir.glob(f"{call_id}_*.wav"):
                return str(filepath.absolute())

            return None

        except Exception as e:
            logger.error(f"Failed to get recording path: {e}")
            return None

    def delete_recording(self, call_id: str) -> bool:
        """
        Delete recording file

        Args:
            call_id: Call ID

        Returns:
            bool: True if deleted
        """
        try:
            filepath = self.get_recording_path(call_id)
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Recording deleted: {filepath}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete recording: {e}")
            return False

    def get_recording_url(self, call_id: str) -> Optional[str]:
        """
        Get URL to access recording (for API response)

        Args:
            call_id: Call ID

        Returns:
            str: URL or None
        """
        filepath = self.get_recording_path(call_id)
        if filepath:
            # Return relative path for API
            return f"/api/v1/recordings/{call_id}"
        return None


# Global storage service instance
local_storage_service = LocalStorageService()
