"""
Text-to-Speech service using OpenAI TTS
"""
from openai import OpenAI
import logging
import io
from typing import Optional

from app.config.settings import settings
from app.core.exceptions import TTSException

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using OpenAI TTS API"""

    def __init__(self):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                organization=settings.OPENAI_ORG_ID
            )
            self.model = settings.TTS_MODEL
            self.voice = settings.TTS_VOICE
            logger.info(f"TTS service initialized successfully with voice: {self.voice}")
        except Exception as e:
            logger.error(f"Failed to initialize TTS service: {e}")
            raise TTSException(f"TTS initialization failed: {e}")

    async def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> bytes:
        """
        Convert text to speech using OpenAI TTS

        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            bytes: Audio data in PCM format (16-bit, 24kHz)

        Raises:
            TTSException: If synthesis fails
        """
        try:
            voice = voice or self.voice

            logger.debug(f"Synthesizing speech: '{text[:50]}...'")

            # Call TTS API
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="pcm"  # Get raw PCM audio
            )

            # Get audio bytes
            audio_bytes = response.content

            logger.info(f"Speech synthesized: {len(audio_bytes)} bytes")

            return audio_bytes

        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            raise TTSException(f"Speech synthesis failed: {e}")

    async def synthesize_speech_streaming(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ):
        """
        Convert text to speech with streaming (for future optimization)

        Args:
            text: Text to convert to speech
            voice: Voice to use
            speed: Speech speed

        Yields:
            bytes: Audio chunks

        Raises:
            TTSException: If synthesis fails
        """
        try:
            voice = voice or self.voice

            logger.debug(f"Synthesizing speech (streaming): '{text[:50]}...'")

            # Call TTS API with streaming
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="pcm"
            )

            # Stream audio chunks
            chunk_size = 4096
            audio_stream = io.BytesIO(response.content)

            while True:
                chunk = audio_stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        except Exception as e:
            logger.error(f"Failed to stream speech synthesis: {e}")
            raise TTSException(f"Speech synthesis streaming failed: {e}")

    async def synthesize_for_phone(
        self,
        text: str,
        target_sample_rate: int = 8000
    ) -> bytes:
        """
        Synthesize speech optimized for phone call (8kHz)

        Args:
            text: Text to convert
            target_sample_rate: Target sample rate (8000 for phone)

        Returns:
            bytes: Audio data in PCM format at target sample rate
        """
        try:
            # Synthesize at 24kHz (OpenAI TTS default for PCM)
            audio_24khz = await self.synthesize_speech(text)

            # Resample to 8kHz if needed
            if target_sample_rate != 24000:
                from app.utils.audio_utils import resample_audio
                audio_resampled = resample_audio(
                    audio_24khz,
                    from_rate=24000,
                    to_rate=target_sample_rate
                )
                return audio_resampled

            return audio_24khz

        except Exception as e:
            logger.error(f"Failed to synthesize for phone: {e}")
            raise TTSException(f"Phone speech synthesis failed: {e}")


# Global TTS service instance
tts_service = TTSService()
