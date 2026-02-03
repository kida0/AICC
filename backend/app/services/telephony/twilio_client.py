"""
Twilio client wrapper for making calls and managing phone operations
"""
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from typing import Optional
import logging

from app.config.settings import settings
from app.core.exceptions import TwilioException

logger = logging.getLogger(__name__)


class TwilioClient:
    """Wrapper class for Twilio API operations"""

    def __init__(self):
        """Initialize Twilio client"""
        try:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.phone_number = settings.TWILIO_PHONE_NUMBER
            logger.info("Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            raise TwilioException(f"Twilio initialization failed: {e}")

    def make_outbound_call(
        self,
        to_number: str,
        call_id: str,
        webhook_url: Optional[str] = None
    ) -> str:
        """
        Initiate an outbound call

        Args:
            to_number: Destination phone number (E.164 format)
            call_id: Internal call ID for tracking
            webhook_url: Optional webhook URL for call events

        Returns:
            str: Twilio Call SID

        Raises:
            TwilioException: If call initiation fails
        """
        try:
            # Construct webhook URL
            if not webhook_url:
                base_url = settings.TWILIO_WEBHOOK_BASE_URL or "http://localhost:8000"
                webhook_url = f"{base_url}/api/v1/webhooks/twilio/voice"

            # Add call_id as query parameter
            webhook_url = f"{webhook_url}?call_id={call_id}"

            logger.info(f"Initiating outbound call to {to_number}")

            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=webhook_url,
                status_callback=f"{settings.TWILIO_WEBHOOK_BASE_URL or 'http://localhost:8000'}/api/v1/webhooks/twilio/call-status?call_id={call_id}",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )

            logger.info(f"Call initiated successfully. SID: {call.sid}")
            return call.sid

        except Exception as e:
            logger.error(f"Failed to initiate call: {e}")
            raise TwilioException(f"Call initiation failed: {e}")

    def generate_twiml_with_stream(self, websocket_url: str) -> str:
        """
        Generate TwiML response to connect call to Media Stream

        Args:
            websocket_url: WebSocket URL for media streaming

        Returns:
            str: TwiML XML string
        """
        try:
            response = VoiceResponse()

            # Initial greeting
            response.say(
                "안녕하세요. 키다의 AI 상담사입니다. 이번주 고객님의 특별 혜택을 확인하세요.",
                language="ko-KR"
            )

            # Connect to media stream
            connect = Connect()
            stream = Stream(url=websocket_url)
            connect.append(stream)
            response.append(connect)

            twiml = str(response)
            logger.info(f"Generated TwiML: {twiml}")
            return twiml

        except Exception as e:
            logger.error(f"Failed to generate TwiML: {e}")
            raise TwilioException(f"TwiML generation failed: {e}")

    def hangup_call(self, call_sid: str) -> bool:
        """
        Terminate an active call

        Args:
            call_sid: Twilio Call SID

        Returns:
            bool: True if successful

        Raises:
            TwilioException: If hangup fails
        """
        try:
            call = self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} terminated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to hang up call {call_sid}: {e}")
            raise TwilioException(f"Hangup failed: {e}")

    def get_call_status(self, call_sid: str) -> dict:
        """
        Get current status of a call

        Args:
            call_sid: Twilio Call SID

        Returns:
            dict: Call status information

        Raises:
            TwilioException: If status retrieval fails
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "from": call.from_,
                "to": call.to,
            }
        except Exception as e:
            logger.error(f"Failed to get call status for {call_sid}: {e}")
            raise TwilioException(f"Status retrieval failed: {e}")


# Global Twilio client instance
twilio_client = TwilioClient()
