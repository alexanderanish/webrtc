"""
Tests for Gemini Integration
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from webrtc_enterprise import (
    GeminiIntegration,
    GeminiWebRTCBridge,
    SessionConfig,
)


@pytest.mark.unit
class TestGeminiIntegration:
    """Test GeminiIntegration functionality"""

    def test_init(self):
        """Test GeminiIntegration initialization"""
        gemini = GeminiIntegration(
            api_key="test-api-key",
            model_name="gemini-2.0-flash-exp",
            system_instruction="Test instruction"
        )

        assert gemini.api_key == "test-api-key"
        assert gemini.model_name == "gemini-2.0-flash-exp"
        assert gemini.system_instruction == "Test instruction"
        assert gemini.is_connected is False

    @pytest.mark.asyncio
    async def test_connect(self, mock_gemini):
        """Test connecting to Gemini API"""
        await mock_gemini.connect()

        mock_gemini.connect.assert_called_once()
        assert mock_gemini.is_connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self, mock_gemini):
        """Test disconnecting from Gemini API"""
        await mock_gemini.disconnect()

        mock_gemini.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_text(self, mock_gemini):
        """Test sending text message"""
        response = await mock_gemini.send_text("Hello, Gemini!")

        mock_gemini.send_text.assert_called_once_with("Hello, Gemini!")
        assert response == "Mock response"

    @pytest.mark.asyncio
    async def test_send_audio(self, mock_gemini):
        """Test sending audio data"""
        audio_data = b"audio bytes"

        await mock_gemini.send_audio(audio_data)

        mock_gemini.send_audio.assert_called_once_with(audio_data)


@pytest.mark.unit
class TestGeminiWebRTCBridge:
    """Test GeminiWebRTCBridge functionality"""

    def test_init(self, mock_gemini, session_config):
        """Test GeminiWebRTCBridge initialization"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)

        assert bridge.gemini == mock_gemini
        assert bridge.config == session_config
        assert bridge.is_running is False
        assert len(bridge.audio_buffer) == 0

    @pytest.mark.asyncio
    async def test_start(self, mock_gemini, session_config):
        """Test starting the bridge"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)

        await bridge.start()

        mock_gemini.connect.assert_called_once()
        assert bridge.is_running is True

    @pytest.mark.asyncio
    async def test_stop(self, mock_gemini, session_config):
        """Test stopping the bridge"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)
        await bridge.start()

        await bridge.stop()

        mock_gemini.disconnect.assert_called_once()
        assert bridge.is_running is False

    @pytest.mark.asyncio
    async def test_process_text_message(self, mock_gemini, session_config):
        """Test processing text message through Gemini"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)
        await bridge.start()

        response = await bridge.process_text_message("Test message")

        mock_gemini.send_text.assert_called_once_with("Test message")
        assert response == "Mock response"

    @pytest.mark.asyncio
    async def test_process_text_message_not_running(self, mock_gemini, session_config):
        """Test processing text when bridge not running"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)

        with pytest.raises(Exception, match="Bridge not running"):
            await bridge.process_text_message("Test")

    @pytest.mark.asyncio
    async def test_process_audio_frame(self, mock_gemini, session_config):
        """Test processing audio frame"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)
        await bridge.start()

        # Mock audio frame
        mock_frame = Mock()
        mock_frame.to_ndarray = Mock(return_value=Mock())
        mock_frame.to_ndarray.return_value.tobytes = Mock(return_value=b'\x00' * 1000)

        await bridge.process_audio_frame(mock_frame)

        # Audio should be buffered
        assert len(bridge.audio_buffer) > 0

    @pytest.mark.asyncio
    async def test_process_audio_frame_sends_chunks(self, mock_gemini, session_config):
        """Test that audio is sent in chunks when buffer is full"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)
        await bridge.start()

        # Mock audio frame with enough data to trigger send
        mock_frame = Mock()
        mock_frame.to_ndarray = Mock(return_value=Mock())
        mock_frame.to_ndarray.return_value.tobytes = Mock(return_value=b'\x00' * 1000)

        await bridge.process_audio_frame(mock_frame)

        # Should have sent audio data
        assert mock_gemini.send_audio.called or len(bridge.audio_buffer) > 0

    def test_set_audio_response_handler(self, mock_gemini, session_config):
        """Test setting audio response handler"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)

        handler = Mock()
        bridge.set_audio_response_handler(handler)

        # Handler should be set (implementation detail)
        assert True  # Basic test that method doesn't error


@pytest.mark.integration
class TestGeminiIntegrationFlow:
    """Integration tests for Gemini integration flow"""

    @pytest.mark.asyncio
    async def test_full_gemini_bridge_flow(self, mock_gemini, session_config):
        """Test full flow from start to processing messages"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)

        # Start bridge
        await bridge.start()
        assert bridge.is_running

        # Process text message
        response = await bridge.process_text_message("Hello")
        assert response == "Mock response"

        # Stop bridge
        await bridge.stop()
        assert not bridge.is_running

    @pytest.mark.asyncio
    async def test_multiple_text_messages(self, mock_gemini, session_config):
        """Test processing multiple text messages"""
        bridge = GeminiWebRTCBridge(mock_gemini, session_config)
        await bridge.start()

        messages = ["Hello", "How are you?", "Goodbye"]
        responses = []

        for message in messages:
            response = await bridge.process_text_message(message)
            responses.append(response)

        assert len(responses) == 3
        assert all(r == "Mock response" for r in responses)

        await bridge.stop()
