"""
WebRTC Signaling Server
Handles WebSocket connections and signaling messages
"""

import json
import logging
import uuid
from typing import Dict, Optional, Callable, Awaitable
from fastapi import WebSocket, WebSocketDisconnect
from .types import SignalingMessage, SessionConfig

logger = logging.getLogger(__name__)


class SignalingServer:
    """Manages WebSocket signaling for WebRTC connections"""

    def __init__(self):
        self.sessions: Dict[str, WebSocket] = {}
        self.message_handlers: Dict[str, Callable] = {}

    def register_handler(
        self,
        message_type: str,
        handler: Callable[[SignalingMessage, str], Awaitable[Optional[SignalingMessage]]],
    ) -> None:
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler

    async def handle_connection(
        self,
        websocket: WebSocket,
        session_config: Optional[SessionConfig] = None,
    ) -> None:
        """Handle WebSocket connection lifecycle"""
        await websocket.accept()

        session_id = session_config.session_id if session_config else str(uuid.uuid4())
        self.sessions[session_id] = websocket

        logger.info(f"Client connected: {session_id}")

        try:
            # Send ready message
            await self.send_message(
                websocket,
                SignalingMessage(type="ready", session_id=session_id),
            )

            # Message loop
            while True:
                try:
                    data = await websocket.receive_text()
                    message = SignalingMessage(**json.loads(data))
                    message.session_id = session_id

                    # Handle message
                    response = await self._handle_message(message, session_id)
                    if response:
                        await self.send_message(websocket, response)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    await self.send_error(websocket, "Invalid message format")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await self.send_error(websocket, str(e))

        except WebSocketDisconnect:
            logger.info(f"Client disconnected: {session_id}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            await self.cleanup_session(session_id)

    async def _handle_message(
        self, message: SignalingMessage, session_id: str
    ) -> Optional[SignalingMessage]:
        """Process incoming signaling messages"""
        handler = self.message_handlers.get(message.type)

        if handler:
            try:
                return await handler(message, session_id)
            except Exception as e:
                logger.error(f"Handler error for {message.type}: {e}")
                return SignalingMessage(
                    type="error",
                    data={"message": str(e)},
                    session_id=session_id,
                )
        else:
            logger.warning(f"No handler for message type: {message.type}")
            return None

    async def send_message(self, websocket: WebSocket, message: SignalingMessage) -> None:
        """Send a signaling message to the client"""
        try:
            await websocket.send_text(message.model_dump_json())
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def send_error(self, websocket: WebSocket, error_message: str) -> None:
        """Send error message to client"""
        await self.send_message(
            websocket,
            SignalingMessage(type="error", data={"message": error_message}),
        )

    async def cleanup_session(self, session_id: str) -> None:
        """Clean up session resources"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        logger.info(f"Session cleaned up: {session_id}")

    def get_session(self, session_id: str) -> Optional[WebSocket]:
        """Get WebSocket for a session"""
        return self.sessions.get(session_id)
