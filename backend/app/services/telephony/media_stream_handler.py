"""
Twilio Media Stream WebSocket handler

Handles real-time audio streaming from Twilio and coordinates the AI pipeline
"""
from fastapi import WebSocket, Depends
import json
import asyncio
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.utils.audio_utils import base64_to_audio, audio_to_base64
from app.api.v1.endpoints.websocket import broadcast_to_call
from app.services.ai.conversation_manager import ConversationManager
from app.services.ai.tts_service import tts_service
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class MediaStreamHandler:
    """
    Handler for Twilio Media Stream WebSocket connection

    Manages the bi-directional audio stream and coordinates:
    - Audio reception from phone
    - STT processing (via ConversationManager)
    - LLM response generation (via ConversationManager)
    - TTS audio generation
    - Audio transmission to phone
    """

    def __init__(self, call_id: str, db: Session):
        """
        Initialize media stream handler

        Args:
            call_id: Internal call ID
            db: Database session
        """
        self.call_id = call_id
        self.db = db
        self.stream_sid: Optional[str] = None
        self.audio_buffer = bytearray()
        self.is_active = False
        self.is_processing = False  # Prevent concurrent processing

        # Audio parameters (Twilio uses 8kHz mu-law)
        self.sample_rate = 8000
        self.encoding = "mulaw"

        # Initialize conversation manager
        self.conversation_manager = ConversationManager(call_id, db)

        logger.info(f"MediaStreamHandler initialized for call {call_id}")

    async def handle_stream(self, websocket: WebSocket):
        """
        Handle Media Stream WebSocket connection

        Args:
            websocket: WebSocket connection from Twilio
        """
        await websocket.accept()
        self.is_active = True

        logger.info(f"Media Stream WebSocket accepted for call {self.call_id}")

        try:
            # Send initial greeting
            await self._send_greeting(websocket)

            while self.is_active:
                # Receive message from Twilio
                message_text = await websocket.receive_text()
                message = json.loads(message_text)

                # Handle different event types
                event = message.get("event")

                if event == "connected":
                    await self._handle_connected(message)

                elif event == "start":
                    await self._handle_start(message)

                elif event == "media":
                    await self._handle_media(message, websocket)

                elif event == "stop":
                    await self._handle_stop(message)
                    break

        except Exception as e:
            logger.error(f"Error in media stream handler: {e}", exc_info=True)
        finally:
            self.is_active = False
            logger.info(f"Media Stream ended for call {self.call_id}")

    async def _handle_connected(self, message: dict):
        """Handle 'connected' event from Twilio"""
        logger.info(f"Media Stream connected: {message}")
        await broadcast_to_call(self.call_id, {
            "type": "media_stream_connected",
            "timestamp": datetime.now().isoformat()
        })

    async def _handle_start(self, message: dict):
        """Handle 'start' event from Twilio"""
        self.stream_sid = message.get("streamSid")
        start_data = message.get("start", {})

        logger.info(f"Media Stream started: SID={self.stream_sid}, Call SID={start_data.get('callSid')}")

        await broadcast_to_call(self.call_id, {
            "type": "media_stream_started",
            "stream_sid": self.stream_sid,
            "timestamp": datetime.now().isoformat()
        })

    async def _handle_media(self, message: dict, websocket: WebSocket):
        """
        Handle 'media' event from Twilio

        This receives audio chunks from the phone call

        Args:
            message: Media message from Twilio
            websocket: WebSocket connection
        """
        media_data = message.get("media", {})
        payload = media_data.get("payload")  # Base64 encoded mu-law audio

        if not payload:
            return

        try:
            # Decode audio from base64 mu-law to PCM
            audio_bytes = base64_to_audio(payload, encoding="mulaw")

            # Add to buffer
            self.audio_buffer.extend(audio_bytes)

            # Process audio when buffer reaches certain size (e.g., 2 seconds)
            # 8kHz * 2 bytes (int16) * 2 seconds = 32000 bytes
            # Longer buffer = better transcription quality
            BUFFER_THRESHOLD = 32000

            if len(self.audio_buffer) >= BUFFER_THRESHOLD and not self.is_processing:
                # Process in background to avoid blocking
                asyncio.create_task(
                    self._process_audio_chunk(bytes(self.audio_buffer), websocket)
                )
                self.audio_buffer.clear()

        except Exception as e:
            logger.error(f"Error handling media: {e}")

    async def _handle_stop(self, message: dict):
        """Handle 'stop' event from Twilio"""
        logger.info(f"Media Stream stopped for call {self.call_id}")

        # Process remaining audio in buffer
        if len(self.audio_buffer) > 8000 and not self.is_processing:  # At least 0.5 seconds
            logger.info("Processing remaining audio in buffer")
            # Note: Can't send response as stream is stopping, just process for transcript
            await self._process_audio_chunk(bytes(self.audio_buffer), None)

        await broadcast_to_call(self.call_id, {
            "type": "media_stream_stopped",
            "timestamp": datetime.now().isoformat()
        })

    async def _send_greeting(self, websocket: WebSocket):
        """
        Send initial greeting when call starts

        Args:
            websocket: WebSocket connection
        """
        try:
            logger.info("Sending initial greeting")

            # Get greeting from conversation manager
            greeting_text = await self.conversation_manager.handle_greeting()

            # Convert to speech
            greeting_audio = await tts_service.synthesize_for_phone(greeting_text)

            # Send to phone
            await self.send_audio_to_phone(greeting_audio, websocket)

            # Broadcast to frontend
            await broadcast_to_call(self.call_id, {
                "type": "transcript",
                "speaker": "ai",
                "text": greeting_text,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error sending greeting: {e}")

    async def _process_audio_chunk(self, audio_bytes: bytes, websocket: Optional[WebSocket]):
        """
        Process accumulated audio chunk through AI pipeline

        Pipeline:
        1. Send audio to STT (Whisper)
        2. Get transcript
        3. Send transcript to LLM (Claude)
        4. Get AI response
        5. Convert response to speech (TTS)
        6. Send audio back to phone

        Args:
            audio_bytes: PCM audio bytes
            websocket: WebSocket connection to send audio back (None if stopping)
        """
        if self.is_processing:
            logger.debug("Already processing, skipping chunk")
            return

        self.is_processing = True

        try:
            logger.info(f"Processing audio chunk: {len(audio_bytes)} bytes")

            # Step 1-4: Process user audio through conversation manager
            # This handles STT, LLM, and saves transcripts
            ai_response_text = await self.conversation_manager.process_user_audio(audio_bytes)

            # Broadcast user transcript to frontend (already saved by conversation manager)
            # The conversation manager handles saving, we just need to broadcast for real-time UI

            if not ai_response_text:
                logger.debug("No response generated, skipping TTS")
                return

            # Broadcast AI response to frontend
            await broadcast_to_call(self.call_id, {
                "type": "transcript",
                "speaker": "ai",
                "text": ai_response_text,
                "timestamp": datetime.now().isoformat()
            })

            # Step 5: Convert AI response to speech (TTS)
            if websocket:  # Only send audio if WebSocket is still active
                logger.debug("Converting AI response to speech")
                ai_audio = await tts_service.synthesize_for_phone(ai_response_text)

                # Step 6: Send audio to phone
                await self.send_audio_to_phone(ai_audio, websocket)

                logger.info(f"AI response sent to phone: '{ai_response_text[:50]}...'")

        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}", exc_info=True)

        finally:
            self.is_processing = False

    async def send_audio_to_phone(self, audio_bytes: bytes, websocket: WebSocket):
        """
        Send audio to the phone via Media Stream

        Args:
            audio_bytes: PCM audio bytes to send (8kHz)
            websocket: WebSocket connection
        """
        try:
            # Split audio into chunks for smoother playback
            CHUNK_SIZE = 4000  # ~0.25 seconds at 8kHz

            for i in range(0, len(audio_bytes), CHUNK_SIZE):
                chunk = audio_bytes[i:i + CHUNK_SIZE]

                # Encode audio to mu-law base64
                base64_audio = audio_to_base64(chunk, encoding="mulaw")

                # Create media message
                media_message = {
                    "event": "media",
                    "streamSid": self.stream_sid,
                    "media": {
                        "payload": base64_audio
                    }
                }

                # Send to Twilio
                await websocket.send_json(media_message)

                # Small delay to prevent overwhelming the stream
                await asyncio.sleep(0.02)

            logger.debug(f"Sent audio to phone: {len(audio_bytes)} bytes in {len(audio_bytes) // CHUNK_SIZE + 1} chunks")

        except Exception as e:
            logger.error(f"Error sending audio to phone: {e}")


# WebSocket endpoint for media stream
from fastapi import APIRouter

media_router = APIRouter(tags=["media-stream"])


@media_router.websocket("/ws/media/{call_id}")
async def media_stream_websocket(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for Twilio Media Stream

    This endpoint receives real-time audio from the phone call and
    coordinates the full AI pipeline (STT → LLM → TTS)

    Args:
        websocket: WebSocket connection from Twilio
        call_id: Call ID
    """
    logger.info(f"Media Stream WebSocket connection requested for call {call_id}")

    # Create database session for this connection
    db = SessionLocal()

    try:
        handler = MediaStreamHandler(call_id, db)
        await handler.handle_stream(websocket)
    finally:
        db.close()
