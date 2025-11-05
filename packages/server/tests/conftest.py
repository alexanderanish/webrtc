"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import Mock, AsyncMock, MagicMock

from webrtc_enterprise import (
    WebRTCServer,
    SignalingServer,
    GeminiIntegration,
    SessionConfig,
    MediaConfig,
)


@pytest.fixture
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def media_config():
    """Default media configuration"""
    return MediaConfig(
        audio_codec="opus",
        audio_sample_rate=48000,
        audio_channels=1,
    )


@pytest.fixture
def session_config():
    """Default session configuration"""
    return SessionConfig(
        session_id="test-session-123",
        use_gemini=False,
        enable_audio=True,
        enable_video=False,
        enable_data_channel=True,
    )


@pytest.fixture
def signaling_server():
    """Create SignalingServer instance"""
    return SignalingServer()


@pytest.fixture
def webrtc_server(media_config, signaling_server):
    """Create WebRTCServer instance"""
    return WebRTCServer(
        media_config=media_config,
        signaling_server=signaling_server,
    )


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.close = AsyncMock()
    websocket.client = Mock()
    websocket.client.host = "127.0.0.1"
    return websocket


@pytest.fixture
def mock_peer_connection():
    """Mock RTCPeerConnection"""
    pc = Mock()
    pc.setRemoteDescription = AsyncMock()
    pc.createAnswer = AsyncMock(return_value=Mock(sdp="answer", type="answer"))
    pc.setLocalDescription = AsyncMock()
    pc.addIceCandidate = AsyncMock()
    pc.close = AsyncMock()
    pc.connectionState = "new"
    pc.localDescription = Mock(sdp="answer", type="answer")
    return pc


@pytest.fixture
def mock_gemini():
    """Mock GeminiIntegration"""
    gemini = Mock(spec=GeminiIntegration)
    gemini.connect = AsyncMock()
    gemini.disconnect = AsyncMock()
    gemini.send_text = AsyncMock(return_value="Mock response")
    gemini.send_audio = AsyncMock()
    gemini.is_connected = True
    return gemini


@pytest.fixture
def mock_media_stream_track():
    """Mock MediaStreamTrack"""
    track = Mock()
    track.kind = "audio"
    track.recv = AsyncMock()
    return track
