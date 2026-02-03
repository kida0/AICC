"""
Twilio webhook endpoints
"""
from fastapi import APIRouter, Depends, Request, Response, Query
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.call import Call
from app.services.telephony.twilio_client import twilio_client
from app.config.settings import settings

router = APIRouter(prefix="/webhooks/twilio", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/voice")
async def voice_webhook(
    request: Request,
    call_id: str = Query(..., description="Internal call ID"),
    db: Session = Depends(get_db)
):
    """
    Twilio voice webhook - called when call is answered

    This endpoint generates TwiML to connect the call to Media Stream

    Args:
        request: FastAPI request object
        call_id: Internal call ID
        db: Database session

    Returns:
        Response: TwiML XML response
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        twilio_call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")

        logger.info(f"Voice webhook called for call {call_id}, status: {call_status}")

        # Update call record
        call = db.query(Call).filter(Call.id == call_id).first()
        if call:
            call.status = "ringing" if call_status == "ringing" else "in_progress"
            if call_status == "in-progress" and not call.started_at:
                call.started_at = datetime.now()
            db.commit()

        # Generate WebSocket URL for Media Stream
        ws_base_url = settings.TWILIO_WEBHOOK_BASE_URL or "http://localhost:8000"
        if ws_base_url.startswith("http"):
            ws_base_url = ws_base_url.replace("http", "ws")
        elif ws_base_url.startswith("https"):
            ws_base_url = ws_base_url.replace("https", "wss")

        websocket_url = f"{ws_base_url}/ws/media/{call_id}"

        # Generate TwiML response
        twiml = twilio_client.generate_twiml_with_stream(websocket_url)

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error in voice webhook: {e}")
        # Return a simple TwiML response to avoid Twilio errors
        simple_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say language="ko-KR">오류가 발생했습니다.</Say></Response>'
        return Response(content=simple_twiml, media_type="application/xml")


@router.post("/call-status")
async def call_status_webhook(
    request: Request,
    call_id: str = Query(..., description="Internal call ID"),
    db: Session = Depends(get_db)
):
    """
    Twilio call status webhook - receives call status updates

    Args:
        request: FastAPI request object
        call_id: Internal call ID
        db: Database session

    Returns:
        dict: Success response
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        twilio_call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        call_duration = form_data.get("CallDuration")

        logger.info(f"Status webhook for call {call_id}: {call_status}")

        # Update call record
        call = db.query(Call).filter(Call.id == call_id).first()

        if not call:
            logger.warning(f"Call {call_id} not found in database")
            return {"status": "ok"}

        # Update status
        status_mapping = {
            "initiated": "initiating",
            "ringing": "ringing",
            "in-progress": "in_progress",
            "answered": "in_progress",
            "completed": "completed",
            "failed": "failed",
            "busy": "failed",
            "no-answer": "failed",
            "canceled": "failed"
        }

        new_status = status_mapping.get(call_status, call_status)
        call.status = new_status

        # Update timestamps
        if call_status == "in-progress" and not call.started_at:
            call.started_at = datetime.now()

        if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
            call.ended_at = datetime.now()
            if call_duration:
                call.duration = int(call_duration)
            elif call.started_at:
                call.duration = int((datetime.now() - call.started_at).total_seconds())

        db.commit()

        logger.info(f"Updated call {call_id} status to {new_status}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error in call status webhook: {e}")
        return {"status": "error", "message": str(e)}
