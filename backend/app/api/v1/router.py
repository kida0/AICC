"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import calls, webhooks, websocket, recordings, transcripts
from app.services.telephony.media_stream_handler import media_router

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include endpoint routers
router.include_router(calls.router)
router.include_router(webhooks.router)
router.include_router(websocket.router)
router.include_router(recordings.router)
router.include_router(transcripts.router)

# Include media stream router (no /api/v1 prefix for WebSocket)
media_ws_router = APIRouter()
media_ws_router.include_router(media_router)
