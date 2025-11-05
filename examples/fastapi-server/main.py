"""
FastAPI WebRTC Server Example
Demonstrates integration with WebRTC Enterprise Server and Gemini API
"""

import os
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import from webrtc_enterprise package
# In production, install via: pip install webrtc-enterprise-server
# For development, use: pip install -e ../../packages/server
import sys
sys.path.insert(0, '../../packages/server/src')

from webrtc_enterprise import (
    WebRTCServer,
    GeminiIntegration,
    GeminiWebRTCBridge,
    SessionConfig,
    MediaConfig,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
webrtc_server: Optional[WebRTCServer] = None
gemini: Optional[GeminiIntegration] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global webrtc_server, gemini

    # Startup
    logger.info("Starting WebRTC server...")

    # Initialize media config
    media_config = MediaConfig(
        audio_codec="opus",
        audio_sample_rate=48000,
        audio_channels=1,
    )

    # Initialize WebRTC server
    webrtc_server = WebRTCServer(media_config=media_config)
    logger.info("WebRTC server initialized")

    # Initialize Gemini if API key is provided
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        gemini = GeminiIntegration(
            api_key=api_key,
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            system_instruction="You are a helpful AI assistant communicating via WebRTC. Be concise and friendly.",
        )
        logger.info("Gemini integration initialized")
    else:
        logger.warning("GEMINI_API_KEY not set, Gemini features disabled")

    yield

    # Shutdown
    logger.info("Shutting down WebRTC server...")
    # Cleanup sessions
    if webrtc_server:
        for session_id in list(webrtc_server.sessions.keys()):
            await webrtc_server.close_session(session_id)


# Create FastAPI app
app = FastAPI(
    title="WebRTC Enterprise Server",
    description="Enterprise-grade WebRTC server with Gemini integration",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "WebRTC Enterprise Server",
        "version": "1.0.0",
        "gemini_enabled": gemini is not None,
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "webrtc_server": webrtc_server is not None,
        "gemini_integration": gemini is not None,
        "active_sessions": len(webrtc_server.sessions) if webrtc_server else 0,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for WebRTC signaling
    Handles client connections and establishes WebRTC sessions
    """
    if not webrtc_server:
        await websocket.close(code=1011, reason="Server not initialized")
        return

    session_id = None
    bridge: Optional[GeminiWebRTCBridge] = None

    try:
        # Accept the WebSocket connection
        await websocket.accept()
        logger.info(f"WebSocket connection accepted from {websocket.client}")

        # Create session configuration
        import uuid
        session_id = str(uuid.uuid4())

        session_config = SessionConfig(
            session_id=session_id,
            use_gemini=gemini is not None,
            enable_audio=True,
            enable_video=False,
            enable_data_channel=True,
        )

        # Create WebRTC session
        session = await webrtc_server.create_session(session_config)
        logger.info(f"Created session: {session_id}")

        # Set up Gemini bridge if available
        if gemini and session_config.use_gemini:
            bridge = GeminiWebRTCBridge(gemini, session_config)
            await bridge.start()

            # Connect audio processing pipeline
            session.on_audio_frame = bridge.process_audio_frame

            # Handle data messages through Gemini
            async def handle_data_message(message: str):
                try:
                    import json
                    data = json.loads(message)

                    if data.get("type") == "text":
                        # Process text through Gemini
                        response = await bridge.process_text_message(data["content"])

                        # Send response back through data channel
                        response_data = json.dumps({
                            "type": "text",
                            "content": response,
                            "timestamp": data.get("timestamp"),
                        })
                        await session.send_data(response_data)

                except Exception as e:
                    logger.error(f"Error handling data message: {e}")

            session.on_data_message = handle_data_message

            logger.info(f"Gemini bridge started for session: {session_id}")

        # Handle WebSocket signaling
        await webrtc_server.signaling.handle_connection(
            websocket,
            session_config,
        )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        # Cleanup
        if bridge:
            await bridge.stop()
        if session_id and webrtc_server:
            await webrtc_server.close_session(session_id)
        logger.info(f"Cleaned up session: {session_id}")


@app.get("/sessions")
async def list_sessions():
    """List active WebRTC sessions"""
    if not webrtc_server:
        return {"sessions": []}

    sessions = []
    for session_id, session in webrtc_server.sessions.items():
        sessions.append({
            "session_id": session_id,
            "state": session.state.value,
            "has_audio": session.audio_track is not None,
            "has_video": session.video_track is not None,
            "has_data_channel": session.data_channel is not None,
        })

    return {"sessions": sessions, "total": len(sessions)}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )
