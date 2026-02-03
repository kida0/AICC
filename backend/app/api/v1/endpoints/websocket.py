"""
WebSocket endpoints for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict
import json
import logging

from app.core.database import get_db
from app.models.call import Call

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

# Active WebSocket connections for call status updates
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/ws/call/{call_id}")
async def call_status_websocket(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for real-time call status updates

    Sends real-time updates about call status, transcripts, etc.

    Args:
        websocket: WebSocket connection
        call_id: Call ID
    """
    await websocket.accept()
    active_connections[call_id] = websocket

    logger.info(f"WebSocket connection established for call {call_id}")

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "call_id": call_id,
            "message": "WebSocket connection established"
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            elif message.get("type") == "subscribe":
                await websocket.send_json({
                    "type": "subscribed",
                    "call_id": call_id
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for call {call_id}")
        active_connections.pop(call_id, None)
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {e}")
        active_connections.pop(call_id, None)
        await websocket.close()


async def broadcast_to_call(call_id: str, message: dict):
    """
    Broadcast a message to the WebSocket connection for a specific call

    Args:
        call_id: Call ID
        message: Message to broadcast (will be JSON encoded)
    """
    if call_id in active_connections:
        try:
            await active_connections[call_id].send_json(message)
        except Exception as e:
            logger.error(f"Failed to broadcast to call {call_id}: {e}")
            active_connections.pop(call_id, None)
