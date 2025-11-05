"""
WebRTC Server Implementation
Manages peer connections and media streams
"""

import asyncio
import logging
import uuid
from typing import Dict, Optional, Callable, Any
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
    MediaStreamTrack,
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder

from .types import SignalingMessage, SessionConfig, MediaConfig, ConnectionState
from .signaling import SignalingServer

logger = logging.getLogger(__name__)


class WebRTCSession:
    """Represents a single WebRTC session"""

    def __init__(
        self,
        session_id: str,
        config: SessionConfig,
        media_config: MediaConfig,
    ):
        self.session_id = session_id
        self.config = config
        self.media_config = media_config
        self.pc = RTCPeerConnection()
        self.state = ConnectionState.NEW
        self.data_channel = None
        self.audio_track: Optional[MediaStreamTrack] = None
        self.video_track: Optional[MediaStreamTrack] = None
        self.on_audio_frame: Optional[Callable] = None
        self.on_video_frame: Optional[Callable] = None
        self.on_data_message: Optional[Callable] = None

        self._setup_peer_connection()

    def _setup_peer_connection(self) -> None:
        """Set up peer connection event handlers"""

        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state: {self.pc.connectionState}")
            self.state = ConnectionState(self.pc.connectionState)

        @self.pc.on("track")
        async def on_track(track: MediaStreamTrack):
            logger.info(f"Track received: {track.kind}")

            if track.kind == "audio":
                self.audio_track = track
                if self.on_audio_frame:
                    asyncio.create_task(self._process_audio_track(track))
            elif track.kind == "video":
                self.video_track = track
                if self.on_video_frame:
                    asyncio.create_task(self._process_video_track(track))

        @self.pc.on("datachannel")
        def on_datachannel(channel):
            logger.info(f"Data channel established: {channel.label}")
            self.data_channel = channel

            @channel.on("message")
            def on_message(message):
                if self.on_data_message:
                    asyncio.create_task(self.on_data_message(message))

    async def _process_audio_track(self, track: MediaStreamTrack) -> None:
        """Process incoming audio frames"""
        while True:
            try:
                frame = await track.recv()
                if self.on_audio_frame:
                    await self.on_audio_frame(frame)
            except Exception as e:
                logger.error(f"Error processing audio frame: {e}")
                break

    async def _process_video_track(self, track: MediaStreamTrack) -> None:
        """Process incoming video frames"""
        while True:
            try:
                frame = await track.recv()
                if self.on_video_frame:
                    await self.on_video_frame(frame)
            except Exception as e:
                logger.error(f"Error processing video frame: {e}")
                break

    async def handle_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming offer and create answer"""
        try:
            # Set remote description
            await self.pc.setRemoteDescription(
                RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
            )

            # Create answer
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)

            return {"sdp": self.pc.localDescription.sdp, "type": self.pc.localDescription.type}
        except Exception as e:
            logger.error(f"Error handling offer: {e}")
            raise

    async def handle_ice_candidate(self, candidate: Dict[str, Any]) -> None:
        """Handle ICE candidate"""
        try:
            ice_candidate = RTCIceCandidate(
                candidate=candidate.get("candidate"),
                sdpMid=candidate.get("sdpMid"),
                sdpMLineIndex=candidate.get("sdpMLineIndex"),
            )
            await self.pc.addIceCandidate(ice_candidate)
        except Exception as e:
            logger.error(f"Error adding ICE candidate: {e}")
            raise

    async def send_data(self, message: str) -> None:
        """Send data through data channel"""
        if self.data_channel and self.data_channel.readyState == "open":
            self.data_channel.send(message)
        else:
            raise Exception("Data channel not open")

    async def close(self) -> None:
        """Close the peer connection"""
        if self.pc:
            await self.pc.close()
        self.state = ConnectionState.CLOSED
        logger.info(f"Session closed: {self.session_id}")


class WebRTCServer:
    """Main WebRTC server managing multiple sessions"""

    def __init__(
        self,
        media_config: Optional[MediaConfig] = None,
        signaling_server: Optional[SignalingServer] = None,
    ):
        self.media_config = media_config or MediaConfig()
        self.signaling = signaling_server or SignalingServer()
        self.sessions: Dict[str, WebRTCSession] = {}

        # Register signaling handlers
        self.signaling.register_handler("offer", self._handle_offer)
        self.signaling.register_handler("ice-candidate", self._handle_ice_candidate)

    async def create_session(
        self, session_config: SessionConfig
    ) -> WebRTCSession:
        """Create a new WebRTC session"""
        session = WebRTCSession(
            session_id=session_config.session_id,
            config=session_config,
            media_config=self.media_config,
        )
        self.sessions[session_config.session_id] = session
        logger.info(f"Session created: {session_config.session_id}")
        return session

    async def _handle_offer(
        self, message: SignalingMessage, session_id: str
    ) -> SignalingMessage:
        """Handle offer from client"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                session = await self.create_session(
                    SessionConfig(session_id=session_id)
                )

            answer = await session.handle_offer(message.data)

            return SignalingMessage(
                type="answer",
                data=answer,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Error handling offer: {e}")
            return SignalingMessage(
                type="error",
                data={"message": str(e)},
                session_id=session_id,
            )

    async def _handle_ice_candidate(
        self, message: SignalingMessage, session_id: str
    ) -> Optional[SignalingMessage]:
        """Handle ICE candidate from client"""
        try:
            session = self.sessions.get(session_id)
            if session:
                await session.handle_ice_candidate(message.data)
            return None
        except Exception as e:
            logger.error(f"Error handling ICE candidate: {e}")
            return SignalingMessage(
                type="error",
                data={"message": str(e)},
                session_id=session_id,
            )

    async def close_session(self, session_id: str) -> None:
        """Close and remove a session"""
        session = self.sessions.get(session_id)
        if session:
            await session.close()
            del self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[WebRTCSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
