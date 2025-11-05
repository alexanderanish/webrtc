"""
Google Gemini Real-time API Integration
Handles bi-directional audio/video streaming with Gemini
"""

import asyncio
import logging
import json
from typing import Optional, Callable, Any, Dict
import google.generativeai as genai
from google.ai.generativelanguage_v1alpha import LiveConfig

from .types import GeminiConfig

logger = logging.getLogger(__name__)


class GeminiIntegration:
    """Integration with Google Gemini real-time API"""

    def __init__(
        self,
        api_key: str,
        config: Optional[GeminiConfig] = None,
    ):
        """
        Initialize Gemini integration

        Args:
            api_key: Google AI API key
            config: Complete Gemini configuration
        """
        self.api_key = api_key
        self.config = config or GeminiConfig()
        self.client = None
        self.session = None
        self.is_connected = False

        # Configure the API
        genai.configure(api_key=api_key)

    def _build_live_config(self) -> Dict[str, Any]:
        """Build LiveConfig from GeminiConfig"""
        live_config = {
            "response_modalities": self.config.response_modalities,
        }

        # Add generation config
        if self.config.generation_config:
            gen_config = {}
            if self.config.generation_config.temperature is not None:
                gen_config["temperature"] = self.config.generation_config.temperature
            if self.config.generation_config.top_p is not None:
                gen_config["top_p"] = self.config.generation_config.top_p
            if self.config.generation_config.top_k is not None:
                gen_config["top_k"] = self.config.generation_config.top_k
            if self.config.generation_config.max_output_tokens is not None:
                gen_config["max_output_tokens"] = self.config.generation_config.max_output_tokens
            if self.config.generation_config.stop_sequences:
                gen_config["stop_sequences"] = self.config.generation_config.stop_sequences
            if self.config.generation_config.presence_penalty is not None:
                gen_config["presence_penalty"] = self.config.generation_config.presence_penalty
            if self.config.generation_config.frequency_penalty is not None:
                gen_config["frequency_penalty"] = self.config.generation_config.frequency_penalty

            if gen_config:
                live_config["generation_config"] = gen_config

        # Add speech config
        if self.config.speech_config:
            speech_config = {}
            if self.config.speech_config.language_code:
                speech_config["language_code"] = self.config.speech_config.language_code

            # Add VAD config
            if self.config.speech_config.vad_config:
                vad_config = {}
                vad = self.config.speech_config.vad_config
                if vad.start_of_speech_sensitivity is not None:
                    vad_config["start_of_speech_sensitivity"] = vad.start_of_speech_sensitivity
                if vad.end_of_speech_sensitivity is not None:
                    vad_config["end_of_speech_sensitivity"] = vad.end_of_speech_sensitivity
                if vad.prefix_padding_ms is not None:
                    vad_config["prefix_padding_ms"] = vad.prefix_padding_ms
                if vad.silence_duration_ms is not None:
                    vad_config["silence_duration_ms"] = vad.silence_duration_ms

                if vad_config:
                    speech_config["vad_config"] = vad_config

            if speech_config:
                live_config["speech_config"] = speech_config

        # Add voice config
        if self.config.voice_config:
            voice_config = {}
            if self.config.voice_config.voice_name:
                voice_config["voice_name"] = self.config.voice_config.voice_name
            voice_config["preemptive_interruption"] = self.config.voice_config.preemptive_interruption

            if voice_config:
                live_config["voice_config"] = voice_config

        # Add transcription config
        if self.config.transcription_config:
            if self.config.transcription_config.enable_input_transcription:
                live_config["input_audio_transcription"] = {}
            if self.config.transcription_config.enable_output_transcription:
                live_config["output_audio_transcription"] = {}

        # Add native audio features
        if self.config.native_audio_config:
            if self.config.native_audio_config.enable_affective_dialog:
                live_config["enable_affective_dialog"] = True
            if self.config.native_audio_config.enable_proactive_audio:
                live_config["proactive_audio"] = True
            if self.config.native_audio_config.thinking_budget is not None:
                live_config["thinking_budget"] = self.config.native_audio_config.thinking_budget

        # Add session management
        if self.config.session_config:
            if self.config.session_config.enable_context_window_compression:
                compression_config = {}
                if self.config.session_config.compression_token_threshold:
                    compression_config["token_threshold"] = self.config.session_config.compression_token_threshold
                live_config["context_window_compression"] = compression_config

            if self.config.session_config.enable_session_resumption:
                if self.config.session_config.session_resumption_handle:
                    live_config["session_resumption"] = {
                        "handle": self.config.session_config.session_resumption_handle
                    }

        # Add media resolution
        live_config["media_resolution"] = self.config.media_resolution

        # Add tools
        if self.config.tool_config:
            tools = []

            if self.config.tool_config.enable_google_search:
                tools.append({"google_search": {}})

            if self.config.tool_config.enable_code_execution:
                tools.append({"code_execution": {}})

            if self.config.tool_config.function_declarations:
                for func_decl in self.config.tool_config.function_declarations:
                    func_tool = {"function_declarations": [func_decl]}
                    if self.config.tool_config.function_behavior == "NON_BLOCKING":
                        func_decl["behavior"] = "NON_BLOCKING"
                    tools.append(func_tool)

            if tools:
                live_config["tools"] = tools

        return live_config

    async def connect(self) -> None:
        """Connect to Gemini real-time API"""
        try:
            # Initialize the model
            model_config = {
                "model": self.config.model_name,
            }

            if self.config.system_instruction:
                model_config["system_instruction"] = self.config.system_instruction

            self.client = genai.GenerativeModel(**model_config)

            # Build and configure live session
            live_config = self._build_live_config()

            # Start live session
            enable_auto_calling = (
                self.config.tool_config.enable_automatic_function_calling
                if self.config.tool_config
                else True
            )

            self.session = self.client.start_chat(
                enable_automatic_function_calling=enable_auto_calling,
            )

            self.is_connected = True
            logger.info(f"Connected to Gemini model: {self.config.model_name}")
            logger.info(f"Live config: {json.dumps(live_config, indent=2)}")

        except Exception as e:
            logger.error(f"Failed to connect to Gemini: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Gemini API"""
        self.is_connected = False
        self.session = None
        logger.info("Disconnected from Gemini")

    async def send_audio(self, audio_data: bytes) -> None:
        """
        Send audio data to Gemini

        Args:
            audio_data: Raw audio bytes (PCM16, 16kHz, mono)
        """
        if not self.is_connected or not self.session:
            raise Exception("Not connected to Gemini")

        try:
            # Send audio to Gemini
            # Note: Actual implementation depends on the Gemini API structure
            # This is a placeholder for the audio streaming interface
            pass
        except Exception as e:
            logger.error(f"Error sending audio to Gemini: {e}")
            raise

    async def send_text(self, text: str) -> str:
        """
        Send text message to Gemini and get response

        Args:
            text: Input text message

        Returns:
            Response text from Gemini
        """
        if not self.session:
            raise Exception("Not connected to Gemini")

        try:
            response = await asyncio.to_thread(
                self.session.send_message, text
            )
            return response.text
        except Exception as e:
            logger.error(f"Error sending text to Gemini: {e}")
            raise

    async def stream_audio_response(
        self, on_audio_chunk: Callable[[bytes], Any]
    ) -> None:
        """
        Stream audio responses from Gemini

        Args:
            on_audio_chunk: Callback for audio chunks
        """
        if not self.is_connected:
            raise Exception("Not connected to Gemini")

        # Placeholder for audio streaming from Gemini
        # This will be implemented based on the actual Gemini streaming API
        pass


class GeminiWebRTCBridge:
    """Bridge between WebRTC session and Gemini API"""

    def __init__(
        self,
        gemini: GeminiIntegration,
    ):
        self.gemini = gemini
        self.audio_buffer = bytearray()
        self.is_running = False

    async def start(self) -> None:
        """Start the bridge"""
        await self.gemini.connect()
        self.is_running = True
        logger.info("Gemini-WebRTC bridge started")

    async def stop(self) -> None:
        """Stop the bridge"""
        self.is_running = False
        await self.gemini.disconnect()
        logger.info("Gemini-WebRTC bridge stopped")

    async def process_audio_frame(self, frame: Any) -> None:
        """
        Process audio frame from WebRTC and send to Gemini

        Args:
            frame: Audio frame from aiortc
        """
        if not self.is_running:
            return

        try:
            # Convert frame to bytes
            # Note: Actual conversion depends on the frame format
            audio_data = frame.to_ndarray().tobytes()

            # Buffer audio data
            self.audio_buffer.extend(audio_data)

            # Send chunks when buffer is large enough (e.g., 20ms of audio)
            chunk_size = 640  # 20ms at 16kHz, mono, 16-bit
            if len(self.audio_buffer) >= chunk_size:
                chunk = bytes(self.audio_buffer[:chunk_size])
                self.audio_buffer = self.audio_buffer[chunk_size:]
                await self.gemini.send_audio(chunk)

        except Exception as e:
            logger.error(f"Error processing audio frame: {e}")

    async def process_text_message(self, message: str) -> str:
        """
        Process text message through Gemini

        Args:
            message: Input text message

        Returns:
            Response from Gemini
        """
        if not self.is_running:
            raise Exception("Bridge not running")

        try:
            response = await self.gemini.send_text(message)
            return response
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            raise

    def set_audio_response_handler(
        self, handler: Callable[[bytes], Any]
    ) -> None:
        """Set handler for audio responses from Gemini"""
        asyncio.create_task(
            self.gemini.stream_audio_response(handler)
        )
