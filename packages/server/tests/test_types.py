"""
Tests for type definitions
"""

import pytest
from pydantic import ValidationError

from webrtc_enterprise.types import (
    ConnectionState,
    SignalingMessage,
    SessionConfig,
    MediaConfig,
    DataChannelMessage,
)


@pytest.mark.unit
class TestTypes:
    """Test type definitions"""

    def test_connection_state_enum(self):
        """Test ConnectionState enum values"""
        assert ConnectionState.NEW == "new"
        assert ConnectionState.CONNECTING == "connecting"
        assert ConnectionState.CONNECTED == "connected"
        assert ConnectionState.DISCONNECTED == "disconnected"
        assert ConnectionState.FAILED == "failed"
        assert ConnectionState.CLOSED == "closed"

    def test_signaling_message_valid(self):
        """Test valid SignalingMessage"""
        message = SignalingMessage(
            type="offer",
            data={"sdp": "test"},
            session_id="123"
        )

        assert message.type == "offer"
        assert message.data["sdp"] == "test"
        assert message.session_id == "123"

    def test_signaling_message_types(self):
        """Test all valid SignalingMessage types"""
        valid_types = ["offer", "answer", "ice-candidate", "error", "ready"]

        for msg_type in valid_types:
            message = SignalingMessage(type=msg_type)
            assert message.type == msg_type

    def test_signaling_message_invalid_type(self):
        """Test invalid SignalingMessage type"""
        with pytest.raises(ValidationError):
            SignalingMessage(type="invalid-type")

    def test_session_config_defaults(self):
        """Test SessionConfig default values"""
        config = SessionConfig(session_id="test")

        assert config.session_id == "test"
        assert config.use_gemini is False
        assert config.gemini_model == "gemini-2.0-flash-exp"
        assert config.enable_audio is True
        assert config.enable_video is False
        assert config.enable_data_channel is True

    def test_session_config_custom_values(self):
        """Test SessionConfig with custom values"""
        config = SessionConfig(
            session_id="custom",
            use_gemini=True,
            gemini_model="gemini-pro",
            enable_audio=False,
            enable_video=True,
            enable_data_channel=False
        )

        assert config.session_id == "custom"
        assert config.use_gemini is True
        assert config.gemini_model == "gemini-pro"
        assert config.enable_audio is False
        assert config.enable_video is True
        assert config.enable_data_channel is False

    def test_media_config_defaults(self):
        """Test MediaConfig default values"""
        config = MediaConfig()

        assert config.audio_codec == "opus"
        assert config.video_codec == "VP8"
        assert config.audio_sample_rate == 48000
        assert config.audio_channels == 1
        assert config.video_width == 1280
        assert config.video_height == 720

    def test_media_config_custom_values(self):
        """Test MediaConfig with custom values"""
        config = MediaConfig(
            audio_codec="pcm",
            video_codec="VP9",
            audio_sample_rate=16000,
            audio_channels=2,
            video_width=1920,
            video_height=1080
        )

        assert config.audio_codec == "pcm"
        assert config.video_codec == "VP9"
        assert config.audio_sample_rate == 16000
        assert config.audio_channels == 2
        assert config.video_width == 1920
        assert config.video_height == 1080

    def test_data_channel_message_text(self):
        """Test DataChannelMessage with text"""
        message = DataChannelMessage(
            type="text",
            content="Hello, world!"
        )

        assert message.type == "text"
        assert message.content == "Hello, world!"

    def test_data_channel_message_json(self):
        """Test DataChannelMessage with JSON"""
        message = DataChannelMessage(
            type="json",
            content={"key": "value"}
        )

        assert message.type == "json"
        assert message.content["key"] == "value"

    def test_data_channel_message_with_timestamp(self):
        """Test DataChannelMessage with timestamp"""
        timestamp = 1234567890
        message = DataChannelMessage(
            type="text",
            content="Test",
            timestamp=timestamp
        )

        assert message.timestamp == timestamp

    def test_data_channel_message_invalid_type(self):
        """Test DataChannelMessage with invalid type"""
        with pytest.raises(ValidationError):
            DataChannelMessage(
                type="invalid",
                content="test"
            )
