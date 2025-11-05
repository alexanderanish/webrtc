"""
Tests for SignalingServer
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock
from fastapi import WebSocketDisconnect

from webrtc_enterprise import SignalingServer, SignalingMessage, SessionConfig


@pytest.mark.unit
class TestSignalingServer:
    """Test SignalingServer functionality"""

    def test_init(self, signaling_server):
        """Test SignalingServer initialization"""
        assert signaling_server is not None
        assert signaling_server.sessions == {}
        assert signaling_server.message_handlers == {}

    def test_register_handler(self, signaling_server):
        """Test registering message handlers"""
        async def test_handler(message, session_id):
            return SignalingMessage(type="answer", session_id=session_id)

        signaling_server.register_handler("offer", test_handler)

        assert "offer" in signaling_server.message_handlers
        assert signaling_server.message_handlers["offer"] == test_handler

    @pytest.mark.asyncio
    async def test_send_message(self, signaling_server, mock_websocket):
        """Test sending signaling message"""
        message = SignalingMessage(
            type="ready",
            session_id="test-123"
        )

        await signaling_server.send_message(mock_websocket, message)

        mock_websocket.send_text.assert_called_once()
        sent_data = mock_websocket.send_text.call_args[0][0]
        assert "ready" in sent_data

    @pytest.mark.asyncio
    async def test_send_error(self, signaling_server, mock_websocket):
        """Test sending error message"""
        await signaling_server.send_error(mock_websocket, "Test error")

        mock_websocket.send_text.assert_called_once()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == "error"
        assert sent_data["data"]["message"] == "Test error"

    @pytest.mark.asyncio
    async def test_handle_connection_sends_ready(self, signaling_server, mock_websocket):
        """Test that handle_connection sends ready message"""
        # Make receive_text raise WebSocketDisconnect immediately
        mock_websocket.receive_text = AsyncMock(side_effect=WebSocketDisconnect())

        try:
            await signaling_server.handle_connection(mock_websocket)
        except WebSocketDisconnect:
            pass

        mock_websocket.accept.assert_called_once()
        # Should have sent ready message
        assert mock_websocket.send_text.called

    @pytest.mark.asyncio
    async def test_handle_message_with_handler(self, signaling_server):
        """Test handling message with registered handler"""
        response_message = SignalingMessage(type="answer", session_id="test")

        async def test_handler(message, session_id):
            return response_message

        signaling_server.register_handler("offer", test_handler)

        message = SignalingMessage(type="offer", session_id="test")
        result = await signaling_server._handle_message(message, "test")

        assert result == response_message

    @pytest.mark.asyncio
    async def test_handle_message_without_handler(self, signaling_server):
        """Test handling message without registered handler"""
        message = SignalingMessage(type="offer", session_id="test")
        result = await signaling_server._handle_message(message, "test")

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_message_handler_error(self, signaling_server):
        """Test error handling in message handler"""
        async def error_handler(message, session_id):
            raise Exception("Handler error")

        signaling_server.register_handler("offer", error_handler)

        message = SignalingMessage(type="offer", session_id="test")
        result = await signaling_server._handle_message(message, "test")

        assert result.type == "error"
        assert "Handler error" in result.data["message"]

    @pytest.mark.asyncio
    async def test_cleanup_session(self, signaling_server, mock_websocket):
        """Test session cleanup"""
        session_id = "test-session"
        signaling_server.sessions[session_id] = mock_websocket

        await signaling_server.cleanup_session(session_id)

        assert session_id not in signaling_server.sessions

    def test_get_session(self, signaling_server, mock_websocket):
        """Test getting session by ID"""
        session_id = "test-session"
        signaling_server.sessions[session_id] = mock_websocket

        result = signaling_server.get_session(session_id)

        assert result == mock_websocket

    def test_get_session_not_found(self, signaling_server):
        """Test getting non-existent session"""
        result = signaling_server.get_session("non-existent")

        assert result is None
