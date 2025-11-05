"""
Google Gemini Real-time API Integration
Handles bi-directional audio/video streaming with Gemini
"""

import asyncio
import logging
import json
from typing import Optional, Callable, Any
import google.generativeai as genai
from google.ai.generativelanguage_v1alpha import LiveConfig

from .types import SessionConfig

logger = logging.getLogger(__name__)


class GeminiIntegration:
    """Integration with Google Gemini real-time API"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        system_instruction: Optional[str] = None,
    ):
        """
        Initialize Gemini integration

        Args:
            api_key: Google AI API key
            model_name: Gemini model to use
            system_instruction: Optional system instruction for the model
        """
        self.api_key = api_key
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.client = None
        self.session = None
        self.is_connected = False

        # Configure the API
        genai.configure(api_key=api_key)

    async def connect(
        self,
        config: Optional[LiveConfig] = None,
    ) -> None:
        """Connect to Gemini real-time API"""
        try:
            # Initialize the model
            model_config = {
                "model": self.model_name,
            }

            if self.system_instruction:
                model_config["system_instruction"] = self.system_instruction

            self.client = genai.GenerativeModel(**model_config)

            # Configure live session
            live_config = config or LiveConfig(
                response_modalities=["AUDIO"],
            )

            # Start live session
            self.session = self.client.start_chat(
                enable_automatic_function_calling=True,
            )

            self.is_connected = True
            logger.info(f"Connected to Gemini model: {self.model_name}")

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
        session_config: SessionConfig,
    ):
        self.gemini = gemini
        self.config = session_config
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
