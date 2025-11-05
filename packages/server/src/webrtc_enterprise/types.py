"""
Type definitions for WebRTC Enterprise Server
"""

from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel


class ConnectionState(str, Enum):
    """WebRTC connection states"""
    NEW = "new"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    CLOSED = "closed"


class SignalingMessage(BaseModel):
    """Signaling message structure"""
    type: Literal["offer", "answer", "ice-candidate", "error", "ready"]
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@dataclass
class SessionConfig:
    """Configuration for a WebRTC session"""
    session_id: str
    use_gemini: bool = False
    gemini_model: str = "gemini-2.0-flash-exp"
    enable_audio: bool = True
    enable_video: bool = False
    enable_data_channel: bool = True


@dataclass
class MediaConfig:
    """Media configuration"""
    audio_codec: str = "opus"
    video_codec: str = "VP8"
    audio_sample_rate: int = 48000
    audio_channels: int = 1
    video_width: int = 1280
    video_height: int = 720


class DataChannelMessage(BaseModel):
    """Data channel message structure"""
    type: Literal["text", "binary", "json"]
    content: Any
    timestamp: Optional[int] = None
