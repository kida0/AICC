"""
Call management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import math
import logging

from app.core.database import get_db
from app.schemas.call import CallInitiate, CallResponse, CallListResponse, CallInitiateResponse
from app.models.call import Call
from app.services.telephony.twilio_client import twilio_client
from app.core.exceptions import TwilioException, InvalidPhoneNumberException
from app.config.settings import settings

router = APIRouter(prefix="/calls", tags=["calls"])
logger = logging.getLogger(__name__)


@router.post("/initiate", response_model=CallInitiateResponse, status_code=201)
async def initiate_call(
    call_data: CallInitiate,
    db: Session = Depends(get_db)
):
    """
    Initiate an outbound call

    Args:
        call_data: Call initiation request data
        db: Database session

    Returns:
        CallInitiateResponse: Call initiation details

    Raises:
        HTTPException: If call initiation fails
    """
    try:
        # Validate phone number (basic validation)
        if not call_data.phone_number.startswith('+'):
            raise InvalidPhoneNumberException("Phone number must be in E.164 format (starting with +)")

        # Create call record in database
        new_call = Call(
            phone_number=call_data.phone_number,
            caller_id=call_data.caller_id or settings.TWILIO_PHONE_NUMBER,
            status="initiating",
            direction="outbound",
            ai_persona=call_data.ai_persona or "customer_support"
        )
        db.add(new_call)
        db.commit()
        db.refresh(new_call)

        logger.info(f"Created call record: {new_call.id}")

        # Initiate call via Twilio
        try:
            twilio_call_sid = twilio_client.make_outbound_call(
                to_number=call_data.phone_number,
                call_id=str(new_call.id)
            )

            # Update call record with Twilio SID
            new_call.twilio_call_sid = twilio_call_sid
            db.commit()

            logger.info(f"Call initiated successfully: {new_call.id}")

        except TwilioException as e:
            # Update call status to failed
            new_call.status = "failed"
            db.commit()

            # Parse Twilio error for better user feedback
            error_message = str(e)
            if "21219" in error_message or "unverified" in error_message.lower():
                raise HTTPException(
                    status_code=400,
                    detail="수신 전화번호가 인증되지 않았습니다. Twilio Trial 계정은 인증된 번호로만 전화할 수 있습니다. Twilio Console에서 번호를 인증하거나 계정을 업그레이드하세요."
                )
            elif "21210" in error_message or "source phone number" in error_message.lower():
                raise HTTPException(
                    status_code=400,
                    detail="발신 번호가 유효하지 않습니다. Twilio Console에서 구매한 전화번호를 .env 파일의 TWILIO_PHONE_NUMBER에 설정하세요."
                )
            elif "21212" in error_message or "not a valid phone number" in error_message.lower():
                raise HTTPException(
                    status_code=400,
                    detail="전화번호 형식이 올바르지 않습니다. E.164 형식(+국가번호포함)으로 입력하세요."
                )
            else:
                raise HTTPException(status_code=500, detail=f"전화 연결에 실패했습니다: {str(e)}")

        # Generate WebSocket URL
        ws_base_url = settings.TWILIO_WEBHOOK_BASE_URL or "ws://localhost:8000"
        if ws_base_url.startswith("http"):
            ws_base_url = ws_base_url.replace("http", "ws")
        websocket_url = f"{ws_base_url}/ws/call/{new_call.id}"

        return CallInitiateResponse(
            call_id=new_call.id,
            status=new_call.status,
            phone_number=new_call.phone_number,
            created_at=new_call.created_at,
            websocket_url=websocket_url
        )

    except InvalidPhoneNumberException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error initiating call: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(call_id: str, db: Session = Depends(get_db)):
    """
    Get call details by ID

    Args:
        call_id: Call ID (UUID)
        db: Database session

    Returns:
        CallResponse: Call details

    Raises:
        HTTPException: If call not found
    """
    call = db.query(Call).filter(Call.id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return call


@router.get("", response_model=CallListResponse)
async def list_calls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List calls with pagination and filtering

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page
        status: Filter by call status
        db: Database session

    Returns:
        CallListResponse: List of calls with pagination info
    """
    # Build query
    query = db.query(Call)

    # Apply filters
    if status:
        query = query.filter(Call.status == status)

    # Get total count
    total = query.count()

    # Calculate pagination
    pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size

    # Get paginated results
    calls = query.order_by(Call.created_at.desc()).offset(offset).limit(page_size).all()

    return CallListResponse(
        items=calls,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.delete("/{call_id}", status_code=204)
async def end_call(call_id: str, db: Session = Depends(get_db)):
    """
    End an active call or delete a call record

    Args:
        call_id: Call ID (UUID)
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: If call not found or termination fails
    """
    call = db.query(Call).filter(Call.id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # If call is in progress, terminate via Twilio
    if call.status == "in_progress" and call.twilio_call_sid:
        try:
            twilio_client.hangup_call(call.twilio_call_sid)
            call.status = "completed"
            call.ended_at = datetime.now()
            db.commit()
        except TwilioException as e:
            raise HTTPException(status_code=500, detail=f"Failed to end call: {str(e)}")

    logger.info(f"Call {call_id} ended successfully")
    return None
