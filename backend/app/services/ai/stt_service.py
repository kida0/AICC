"""
Speech-to-Text service using OpenAI Whisper
"""
import openai
from openai import OpenAI
import logging
import io
from typing import Optional

from app.config.settings import settings
from app.core.exceptions import STTException

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service using OpenAI Whisper API"""

    def __init__(self):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                organization=settings.OPENAI_ORG_ID
            )
            self.model = settings.WHISPER_MODEL
            logger.info("STT service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize STT service: {e}")
            raise STTException(f"STT initialization failed: {e}")

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        language: str = "ko",
        prompt: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio to text using Whisper

        Args:
            audio_bytes: PCM audio bytes (16-bit, 8kHz or higher)
            language: Language code (default: 'ko' for Korean)
            prompt: Optional prompt to guide transcription

        Returns:
            dict: Transcription result with text and confidence
            {
                "text": str,
                "language": str,
                "duration": float
            }

        Raises:
            STTException: If transcription fails
        """
        try:
            # Create a file-like object from bytes
            # Whisper API expects WAV format, so we need to add WAV header
            audio_file = self._create_wav_file(audio_bytes)

            logger.debug(f"Transcribing audio: {len(audio_bytes)} bytes")

            # Call Whisper API
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                prompt=prompt,
                response_format="verbose_json"
            )

            # Extract text and metadata
            text = response.text.strip()
            duration = getattr(response, 'duration', 0)
            detected_language = getattr(response, 'language', language)

            logger.info(f"Transcription completed: '{text[:50]}...'")

            return {
                "text": text,
                "language": detected_language,
                "duration": duration
            }

        except openai.APIError as e:
            logger.error(f"OpenAI API error during transcription: {e}")
            raise STTException(f"Transcription failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}")
            raise STTException(f"Transcription failed: {e}")

    def _create_wav_file(self, pcm_bytes: bytes, sample_rate: int = 8000, channels: int = 1) -> io.BytesIO:
        """
        Create WAV file from PCM bytes

        Args:
            pcm_bytes: PCM audio bytes (16-bit signed integers)
            sample_rate: Sample rate in Hz
            channels: Number of audio channels

        Returns:
            io.BytesIO: WAV file as file-like object
        """
        import struct

        # Calculate sizes
        byte_rate = sample_rate * channels * 2  # 2 bytes per sample (16-bit)
        block_align = channels * 2
        data_size = len(pcm_bytes)
        file_size = 36 + data_size

        # Create WAV header
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',           # ChunkID
            file_size,         # ChunkSize
            b'WAVE',           # Format
            b'fmt ',           # Subchunk1ID
            16,                # Subchunk1Size (PCM)
            1,                 # AudioFormat (PCM)
            channels,          # NumChannels
            sample_rate,       # SampleRate
            byte_rate,         # ByteRate
            block_align,       # BlockAlign
            16,                # BitsPerSample
            b'data',           # Subchunk2ID
            data_size          # Subchunk2Size
        )

        # Combine header and PCM data
        wav_file = io.BytesIO()
        wav_file.write(wav_header)
        wav_file.write(pcm_bytes)
        wav_file.seek(0)
        wav_file.name = "audio.wav"  # Required by OpenAI API

        return wav_file

    async def transcribe_audio_streaming(
        self,
        audio_bytes: bytes,
        language: str = "ko"
    ) -> str:
        """
        Simplified transcription for real-time streaming

        Args:
            audio_bytes: PCM audio bytes
            language: Language code

        Returns:
            str: Transcribed text
        """
        result = await self.transcribe_audio(audio_bytes, language=language)
        return result["text"]


# Global STT service instance
stt_service = STTService()
