"""
Enterprise WebRTC Server Library
"""

from .server import WebRTCServer
from .signaling import SignalingServer
from .gemini_integration import GeminiIntegration, GeminiWebRTCBridge
from .types import (
    SignalingMessage,
    SessionConfig,
    MediaConfig,
    ConnectionState,
    GeminiConfig,
    GeminiGenerationConfig,
    GeminiVoiceConfig,
    GeminiVADConfig,
    GeminiSpeechConfig,
    GeminiTranscriptionConfig,
    GeminiNativeAudioConfig,
    GeminiSessionConfig,
    GeminiToolConfig,
    gemini_config_from_dict,
)

__version__ = "1.0.0"
__all__ = [
    "WebRTCServer",
    "SignalingServer",
    "GeminiIntegration",
    "GeminiWebRTCBridge",
    "SignalingMessage",
    "SessionConfig",
    "MediaConfig",
    "ConnectionState",
    "GeminiConfig",
    "GeminiGenerationConfig",
    "GeminiVoiceConfig",
    "GeminiVADConfig",
    "GeminiSpeechConfig",
    "GeminiTranscriptionConfig",
    "GeminiNativeAudioConfig",
    "GeminiSessionConfig",
    "GeminiToolConfig",
    "gemini_config_from_dict",
]
