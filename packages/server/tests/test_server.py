"""
Tests for WebRTCServer
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from webrtc_enterprise import (
    WebRTCServer,
    WebRTCSession,
    SessionConfig,
    MediaConfig,
    SignalingMessage,
    ConnectionState,
)


@pytest.mark.unit
class TestWebRTCSession:
    """Test WebRTCSession functionality"""

    def test_init(self, session_config, media_config):
        """Test WebRTCSession initialization"""
        session = WebRTCSession(
            session_id=session_config.session_id,
            config=session_config,
            media_config=media_config,
        )

        assert session.session_id == session_config.session_id
        assert session.state == ConnectionState.NEW
        assert session.pc is not None

    @pytest.mark.asyncio
    async def test_handle_offer(self, session_config, media_config, mock_peer_connection):
        """Test handling SDP offer"""
        with patch('webrtc_enterprise.server.RTCPeerConnection', return_value=mock_peer_connection):
            session = WebRTCSession(
                session_id=session_config.session_id,
                config=session_config,
                media_config=media_config,
            )
            session.pc = mock_peer_connection

            offer = {"sdp": "offer-sdp", "type": "offer"}
            answer = await session.handle_offer(offer)

            mock_peer_connection.setRemoteDescription.assert_called_once()
            mock_peer_connection.createAnswer.assert_called_once()
            mock_peer_connection.setLocalDescription.assert_called_once()
            assert answer["sdp"] == "answer"
            assert answer["type"] == "answer"

    @pytest.mark.asyncio
    async def test_handle_ice_candidate(self, session_config, media_config, mock_peer_connection):
        """Test handling ICE candidate"""
        with patch('webrtc_enterprise.server.RTCPeerConnection', return_value=mock_peer_connection):
            session = WebRTCSession(
                session_id=session_config.session_id,
                config=session_config,
                media_config=media_config,
            )
            session.pc = mock_peer_connection

            candidate = {
                "candidate": "candidate:123",
                "sdpMid": "0",
                "sdpMLineIndex": 0
            }

            await session.handle_ice_candidate(candidate)

            mock_peer_connection.addIceCandidate.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_data(self, session_config, media_config):
        """Test sending data through data channel"""
        session = WebRTCSession(
            session_id=session_config.session_id,
            config=session_config,
            media_config=media_config,
        )

        # Mock data channel
        session.data_channel = Mock()
        session.data_channel.readyState = "open"
        session.data_channel.send = Mock()

        await session.send_data("Test message")

        session.data_channel.send.assert_called_once_with("Test message")

    @pytest.mark.asyncio
    async def test_send_data_channel_not_open(self, session_config, media_config):
        """Test sending data when channel not open"""
        session = WebRTCSession(
            session_id=session_config.session_id,
            config=session_config,
            media_config=media_config,
        )

        session.data_channel = Mock()
        session.data_channel.readyState = "closed"

        with pytest.raises(Exception, match="Data channel not open"):
            await session.send_data("Test message")

    @pytest.mark.asyncio
    async def test_close(self, session_config, media_config, mock_peer_connection):
        """Test closing session"""
        with patch('webrtc_enterprise.server.RTCPeerConnection', return_value=mock_peer_connection):
            session = WebRTCSession(
                session_id=session_config.session_id,
                config=session_config,
                media_config=media_config,
            )
            session.pc = mock_peer_connection

            await session.close()

            mock_peer_connection.close.assert_called_once()
            assert session.state == ConnectionState.CLOSED


@pytest.mark.unit
class TestWebRTCServer:
    """Test WebRTCServer functionality"""

    def test_init(self, webrtc_server):
        """Test WebRTCServer initialization"""
        assert webrtc_server is not None
        assert webrtc_server.sessions == {}
        assert webrtc_server.signaling is not None

    @pytest.mark.asyncio
    async def test_create_session(self, webrtc_server, session_config):
        """Test creating a WebRTC session"""
        session = await webrtc_server.create_session(session_config)

        assert session.session_id == session_config.session_id
        assert session_config.session_id in webrtc_server.sessions
        assert webrtc_server.sessions[session_config.session_id] == session

    @pytest.mark.asyncio
    async def test_handle_offer(self, webrtc_server, session_config):
        """Test handling offer message"""
        message = SignalingMessage(
            type="offer",
            data={"sdp": "offer-sdp", "type": "offer"},
            session_id=session_config.session_id
        )

        with patch.object(WebRTCSession, 'handle_offer', new_callable=AsyncMock) as mock_handle:
            mock_handle.return_value = {"sdp": "answer", "type": "answer"}

            response = await webrtc_server._handle_offer(message, session_config.session_id)

            assert response.type == "answer"
            assert response.data["sdp"] == "answer"

    @pytest.mark.asyncio
    async def test_handle_ice_candidate(self, webrtc_server, session_config):
        """Test handling ICE candidate message"""
        # Create session first
        await webrtc_server.create_session(session_config)

        message = SignalingMessage(
            type="ice-candidate",
            data={"candidate": "candidate:123"},
            session_id=session_config.session_id
        )

        with patch.object(WebRTCSession, 'handle_ice_candidate', new_callable=AsyncMock):
            response = await webrtc_server._handle_ice_candidate(
                message,
                session_config.session_id
            )

            assert response is None  # ICE candidate doesn't return response

    @pytest.mark.asyncio
    async def test_close_session(self, webrtc_server, session_config):
        """Test closing a session"""
        session = await webrtc_server.create_session(session_config)

        with patch.object(session, 'close', new_callable=AsyncMock) as mock_close:
            await webrtc_server.close_session(session_config.session_id)

            mock_close.assert_called_once()
            assert session_config.session_id not in webrtc_server.sessions

    def test_get_session(self, webrtc_server, session_config):
        """Test getting session by ID"""
        # Manually add session
        mock_session = Mock()
        webrtc_server.sessions[session_config.session_id] = mock_session

        result = webrtc_server.get_session(session_config.session_id)

        assert result == mock_session

    def test_get_session_not_found(self, webrtc_server):
        """Test getting non-existent session"""
        result = webrtc_server.get_session("non-existent")

        assert result is None


@pytest.mark.integration
class TestWebRTCServerIntegration:
    """Integration tests for WebRTCServer"""

    @pytest.mark.asyncio
    async def test_full_connection_flow(self, webrtc_server, session_config):
        """Test full connection flow from offer to answer"""
        # Create session
        session = await webrtc_server.create_session(session_config)

        # Mock peer connection methods
        with patch.object(session, 'handle_offer', new_callable=AsyncMock) as mock_offer:
            mock_offer.return_value = {"sdp": "answer", "type": "answer"}

            # Send offer
            offer_message = SignalingMessage(
                type="offer",
                data={"sdp": "offer", "type": "offer"},
                session_id=session_config.session_id
            )

            response = await webrtc_server._handle_offer(
                offer_message,
                session_config.session_id
            )

            assert response.type == "answer"
            mock_offer.assert_called_once()

        # Clean up
        await webrtc_server.close_session(session_config.session_id)
