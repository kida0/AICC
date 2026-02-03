"""
Conversation state manager

Manages conversation state, history, and coordinates AI pipeline
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.models.call import Call
from app.models.transcript import Transcript
from app.services.ai.stt_service import stt_service
from app.services.ai.llm_service import llm_service

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation state for a single call

    Coordinates:
    - Conversation history
    - Turn-taking
    - Context management
    - Database persistence
    """

    def __init__(self, call_id: str, db: Session):
        """
        Initialize conversation manager

        Args:
            call_id: Call ID
            db: Database session
        """
        self.call_id = call_id
        self.db = db

        # Conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.is_ai_speaking = False
        self.turn_count = 0

        # Context window management (keep last N turns)
        self.max_history_turns = 10

        logger.info(f"ConversationManager initialized for call {call_id}")

    async def process_user_audio(self, audio_bytes: bytes) -> Optional[str]:
        """
        Process user audio through STT and generate AI response

        Args:
            audio_bytes: User's audio (PCM format)

        Returns:
            str: AI response text (None if transcription is empty)
        """
        try:
            # Step 1: Transcribe user audio (STT)
            logger.debug(f"Transcribing user audio for call {self.call_id}")
            transcription = await stt_service.transcribe_audio_streaming(audio_bytes)

            # Skip if transcription is empty or too short
            if not transcription or len(transcription.strip()) < 2:
                logger.debug("Transcription too short, skipping")
                return None

            logger.info(f"User said: '{transcription}'")

            # Save user transcript to database
            await self._save_transcript(
                speaker="user",
                text=transcription,
                confidence=0.95  # Whisper doesn't provide confidence, use default
            )

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": transcription
            })

            # Step 2: Generate AI response (LLM)
            logger.debug(f"Generating AI response for call {self.call_id}")

            # Trim history if too long
            history_for_llm = self._get_trimmed_history()

            ai_response = await llm_service.generate_response(
                user_message=transcription,
                conversation_history=history_for_llm
            )

            logger.info(f"AI response: '{ai_response}'")

            # Save AI transcript to database
            await self._save_transcript(
                speaker="ai",
                text=ai_response,
                confidence=1.0
            )

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })

            self.turn_count += 1

            return ai_response

        except Exception as e:
            logger.error(f"Error processing user audio: {e}")
            # Return a fallback response
            return "죄송합니다. 잠시 문제가 발생했습니다. 다시 한 번 말씀해 주시겠어요?"

    def _get_trimmed_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history trimmed to max length

        Returns:
            List[Dict]: Trimmed conversation history
        """
        # Keep only recent turns (within max_history_turns)
        max_messages = self.max_history_turns * 2  # user + assistant per turn

        if len(self.conversation_history) > max_messages:
            return self.conversation_history[-max_messages:]

        return self.conversation_history

    async def _save_transcript(
        self,
        speaker: str,
        text: str,
        confidence: float
    ):
        """
        Save transcript to database

        Args:
            speaker: 'user' or 'ai'
            text: Transcript text
            confidence: Confidence score
        """
        try:
            transcript = Transcript(
                call_id=self.call_id,
                speaker=speaker,
                text=text,
                timestamp=datetime.now(),
                confidence=confidence
            )

            self.db.add(transcript)
            self.db.commit()

            logger.debug(f"Saved transcript: {speaker} - '{text[:30]}...'")

        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
            self.db.rollback()

    def get_conversation_summary(self) -> Dict:
        """
        Get conversation summary

        Returns:
            dict: Conversation summary with statistics
        """
        user_turns = sum(1 for msg in self.conversation_history if msg["role"] == "user")
        ai_turns = sum(1 for msg in self.conversation_history if msg["role"] == "assistant")

        return {
            "call_id": self.call_id,
            "total_turns": self.turn_count,
            "user_turns": user_turns,
            "ai_turns": ai_turns,
            "conversation_length": len(self.conversation_history)
        }

    async def handle_greeting(self) -> str:
        """
        Generate initial greeting when call starts

        Returns:
            str: Greeting message
        """
        greeting = "안녕하세요! 무엇을 도와드릴까요?"

        # Save greeting to database
        await self._save_transcript(
            speaker="ai",
            text=greeting,
            confidence=1.0
        )

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })

        return greeting
