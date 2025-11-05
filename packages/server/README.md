# WebRTC Enterprise Server

Python library for building WebRTC servers with FastAPI and Gemini integration.

## Installation

```bash
pip install webrtc-enterprise-server
```

## Quick Start

```python
from fastapi import FastAPI, WebSocket
from webrtc_enterprise import (
    WebRTCServer,
    GeminiIntegration,
    SessionConfig,
    GeminiWebRTCBridge,
)

app = FastAPI()

# Initialize components
webrtc_server = WebRTCServer()
gemini = GeminiIntegration(api_key="your-api-key")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept connection
    await websocket.accept()

    # Create session
    session_config = SessionConfig(
        session_id="unique-session-id",
        use_gemini=True,
    )

    session = await webrtc_server.create_session(session_config)

    # Set up Gemini bridge
    bridge = GeminiWebRTCBridge(gemini, session_config)
    await bridge.start()

    # Connect audio processing
    session.on_audio_frame = bridge.process_audio_frame

    # Handle signaling
    await webrtc_server.signaling.handle_connection(
        websocket,
        session_config,
    )
```

## Features

- WebRTC peer connection management with aiortc
- WebSocket signaling server
- Google Gemini real-time API integration
- Audio/video processing pipeline
- Data channel support
- Session management
- Type-safe with Pydantic

## API Reference

See the [documentation](../../docs/server-api.md) for detailed API reference.
