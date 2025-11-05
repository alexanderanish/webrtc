"""
Type definitions for WebRTC Enterprise Server
"""

from typing import Optional, Dict, Any, Literal, List
from dataclasses import dataclass, field
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
    type: Literal["offer", "answer", "ice-candidate", "error", "ready", "config"]
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    gemini_config: Optional[Dict[str, Any]] = None  # Gemini configuration from client


@dataclass
class GeminiGenerationConfig:
    """Gemini generation configuration"""
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 40
    max_output_tokens: Optional[int] = 8192
    candidate_count: Optional[int] = 1
    stop_sequences: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None


@dataclass
class GeminiVoiceConfig:
    """Gemini voice configuration for audio output"""
    voice_name: Optional[str] = None  # Options: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr
    preemptive_interruption: bool = True


@dataclass
class GeminiVADConfig:
    """Voice Activity Detection configuration"""
    start_of_speech_sensitivity: Optional[float] = None  # 0.0 to 1.0
    end_of_speech_sensitivity: Optional[float] = None  # 0.0 to 1.0
    prefix_padding_ms: Optional[int] = None  # milliseconds
    silence_duration_ms: Optional[int] = None  # milliseconds


@dataclass
class GeminiSpeechConfig:
    """Gemini speech configuration for audio input"""
    language_code: Optional[str] = None  # BCP-47 format, e.g., "en-US", "de-DE", "ja-JP"
    vad_config: Optional[GeminiVADConfig] = None


@dataclass
class GeminiTranscriptionConfig:
    """Audio transcription configuration"""
    enable_input_transcription: bool = False
    enable_output_transcription: bool = False


@dataclass
class GeminiNativeAudioConfig:
    """Native audio model specific features"""
    enable_affective_dialog: bool = False  # Emotion-aware dialogue
    enable_proactive_audio: bool = False  # Proactive responses
    thinking_budget: Optional[int] = None  # Thinking time in seconds, 0 to disable


@dataclass
class GeminiSessionConfig:
    """Session management configuration"""
    enable_context_window_compression: bool = False
    compression_token_threshold: Optional[int] = None
    enable_session_resumption: bool = False
    session_resumption_handle: Optional[str] = None


@dataclass
class GeminiToolConfig:
    """Gemini function calling/tool configuration"""
    # Function calling
    function_declarations: Optional[List[Dict[str, Any]]] = None
    enable_automatic_function_calling: bool = True
    function_behavior: str = "BLOCKING"  # Options: "BLOCKING", "NON_BLOCKING"
    response_scheduling: str = "INTERRUPT"  # Options: "INTERRUPT", "WHEN_IDLE", "SILENT"

    # Built-in tools
    enable_code_execution: bool = False
    enable_google_search: bool = False
    enable_url_context: bool = False


@dataclass
class GeminiConfig:
    """Complete Gemini API configuration"""
    # Model configuration
    model_name: str = "gemini-2.0-flash-exp"
    system_instruction: Optional[str] = None

    # Response configuration
    response_modalities: List[str] = field(default_factory=lambda: ["AUDIO"])
    media_resolution: str = "medium"  # Options: "low", "medium", "high"

    # Generation settings
    generation_config: Optional[GeminiGenerationConfig] = None

    # Voice and speech settings
    voice_config: Optional[GeminiVoiceConfig] = None
    speech_config: Optional[GeminiSpeechConfig] = None

    # Transcription settings
    transcription_config: Optional[GeminiTranscriptionConfig] = None

    # Native audio features (for native audio models only)
    native_audio_config: Optional[GeminiNativeAudioConfig] = None

    # Session management
    session_config: Optional[GeminiSessionConfig] = None

    # Tools and function calling
    tool_config: Optional[GeminiToolConfig] = None


@dataclass
class SessionConfig:
    """Configuration for a WebRTC session"""
    session_id: str
    use_gemini: bool = False
    gemini_config: Optional[GeminiConfig] = None
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


def gemini_config_from_dict(data: Dict[str, Any]) -> GeminiConfig:
    """Convert dictionary to GeminiConfig"""
    config = GeminiConfig()

    # Model configuration
    if "model_name" in data:
        config.model_name = data["model_name"]
    if "system_instruction" in data:
        config.system_instruction = data["system_instruction"]

    # Response configuration
    if "response_modalities" in data:
        config.response_modalities = data["response_modalities"]
    if "media_resolution" in data:
        config.media_resolution = data["media_resolution"]

    # Generation config
    if "generation_config" in data:
        gc_data = data["generation_config"]
        config.generation_config = GeminiGenerationConfig(
            temperature=gc_data.get("temperature"),
            top_p=gc_data.get("top_p"),
            top_k=gc_data.get("top_k"),
            max_output_tokens=gc_data.get("max_output_tokens"),
            candidate_count=gc_data.get("candidate_count"),
            stop_sequences=gc_data.get("stop_sequences"),
            presence_penalty=gc_data.get("presence_penalty"),
            frequency_penalty=gc_data.get("frequency_penalty"),
        )

    # Voice config
    if "voice_config" in data:
        vc_data = data["voice_config"]
        config.voice_config = GeminiVoiceConfig(
            voice_name=vc_data.get("voice_name"),
            preemptive_interruption=vc_data.get("preemptive_interruption", True),
        )

    # Speech config
    if "speech_config" in data:
        sc_data = data["speech_config"]
        vad_config = None
        if "vad_config" in sc_data:
            vad_data = sc_data["vad_config"]
            vad_config = GeminiVADConfig(
                start_of_speech_sensitivity=vad_data.get("start_of_speech_sensitivity"),
                end_of_speech_sensitivity=vad_data.get("end_of_speech_sensitivity"),
                prefix_padding_ms=vad_data.get("prefix_padding_ms"),
                silence_duration_ms=vad_data.get("silence_duration_ms"),
            )
        config.speech_config = GeminiSpeechConfig(
            language_code=sc_data.get("language_code"),
            vad_config=vad_config,
        )

    # Transcription config
    if "transcription_config" in data:
        tc_data = data["transcription_config"]
        config.transcription_config = GeminiTranscriptionConfig(
            enable_input_transcription=tc_data.get("enable_input_transcription", False),
            enable_output_transcription=tc_data.get("enable_output_transcription", False),
        )

    # Native audio config
    if "native_audio_config" in data:
        na_data = data["native_audio_config"]
        config.native_audio_config = GeminiNativeAudioConfig(
            enable_affective_dialog=na_data.get("enable_affective_dialog", False),
            enable_proactive_audio=na_data.get("enable_proactive_audio", False),
            thinking_budget=na_data.get("thinking_budget"),
        )

    # Session config
    if "session_config" in data:
        sess_data = data["session_config"]
        config.session_config = GeminiSessionConfig(
            enable_context_window_compression=sess_data.get("enable_context_window_compression", False),
            compression_token_threshold=sess_data.get("compression_token_threshold"),
            enable_session_resumption=sess_data.get("enable_session_resumption", False),
            session_resumption_handle=sess_data.get("session_resumption_handle"),
        )

    # Tool config
    if "tool_config" in data:
        tool_data = data["tool_config"]
        config.tool_config = GeminiToolConfig(
            function_declarations=tool_data.get("function_declarations"),
            enable_automatic_function_calling=tool_data.get("enable_automatic_function_calling", True),
            function_behavior=tool_data.get("function_behavior", "BLOCKING"),
            response_scheduling=tool_data.get("response_scheduling", "INTERRUPT"),
            enable_code_execution=tool_data.get("enable_code_execution", False),
            enable_google_search=tool_data.get("enable_google_search", False),
            enable_url_context=tool_data.get("enable_url_context", False),
        )

    return config
