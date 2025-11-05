# Server API Reference

## WebRTCServer

Main server class for managing WebRTC sessions.

### Constructor

```python
WebRTCServer(
    media_config: Optional[MediaConfig] = None,
    signaling_server: Optional[SignalingServer] = None
)
```

**Parameters:**

- `media_config`: Media configuration (codec, sample rate, etc.)
- `signaling_server`: Custom signaling server instance

**Example:**

```python
from webrtc_enterprise import WebRTCServer, MediaConfig

media_config = MediaConfig(
    audio_codec="opus",
    audio_sample_rate=48000,
    audio_channels=1
)

server = WebRTCServer(media_config=media_config)
```

### Methods

#### create_session(session_config)

Create a new WebRTC session.

```python
await server.create_session(
    session_config: SessionConfig
) -> WebRTCSession
```

**Parameters:**

```python
SessionConfig(
    session_id: str,
    use_gemini: bool = False,
    gemini_model: str = "gemini-2.0-flash-exp",
    enable_audio: bool = True,
    enable_video: bool = False,
    enable_data_channel: bool = True
)
```

**Example:**

```python
session = await server.create_session(
    SessionConfig(
        session_id="unique-id",
        use_gemini=True,
        enable_audio=True
    )
)
```

#### get_session(session_id)

Get session by ID.

```python
session = server.get_session(session_id: str) -> Optional[WebRTCSession]
```

#### close_session(session_id)

Close and remove a session.

```python
await server.close_session(session_id: str) -> None
```

## WebRTCSession

Represents a single WebRTC session.

### Attributes

- `session_id` (str): Unique session identifier
- `state` (ConnectionState): Current connection state
- `audio_track` (MediaStreamTrack): Audio track if available
- `video_track` (MediaStreamTrack): Video track if available
- `data_channel` (RTCDataChannel): Data channel if available

### Event Handlers

#### on_audio_frame

Callback for processing audio frames.

```python
async def process_audio(frame):
    # Process audio frame
    pass

session.on_audio_frame = process_audio
```

#### on_video_frame

Callback for processing video frames.

```python
async def process_video(frame):
    # Process video frame
    pass

session.on_video_frame = process_video
```

#### on_data_message

Callback for data channel messages.

```python
async def handle_message(message: str):
    # Handle data message
    pass

session.on_data_message = handle_message
```

### Methods

#### handle_offer(offer)

Handle SDP offer from client.

```python
answer = await session.handle_offer(offer: Dict[str, Any]) -> Dict[str, Any]
```

#### handle_ice_candidate(candidate)

Handle ICE candidate from client.

```python
await session.handle_ice_candidate(candidate: Dict[str, Any]) -> None
```

#### send_data(message)

Send data through data channel.

```python
await session.send_data(message: str) -> None
```

#### close()

Close the session.

```python
await session.close() -> None
```

## SignalingServer

WebSocket signaling server.

### Methods

#### register_handler(message_type, handler)

Register handler for signaling messages.

```python
async def handle_offer(message: SignalingMessage, session_id: str):
    # Handle offer
    return SignalingMessage(type="answer", data=answer)

signaling.register_handler("offer", handle_offer)
```

#### handle_connection(websocket, session_config)

Handle WebSocket connection.

```python
await signaling.handle_connection(
    websocket: WebSocket,
    session_config: Optional[SessionConfig] = None
) -> None
```

## GeminiIntegration

Integration with Google Gemini real-time API.

### Constructor

```python
GeminiIntegration(
    api_key: str,
    model_name: str = "gemini-2.0-flash-exp",
    system_instruction: Optional[str] = None
)
```

**Example:**

```python
gemini = GeminiIntegration(
    api_key="your-api-key",
    model_name="gemini-2.0-flash-exp",
    system_instruction="You are a helpful assistant."
)
```

### Methods

#### connect(config)

Connect to Gemini API.

```python
await gemini.connect(config: Optional[LiveConfig] = None) -> None
```

#### disconnect()

Disconnect from Gemini API.

```python
await gemini.disconnect() -> None
```

#### send_text(text)

Send text message and get response.

```python
response = await gemini.send_text(text: str) -> str
```

**Example:**

```python
response = await gemini.send_text("Hello, how are you?")
print(response)
```

#### send_audio(audio_data)

Send audio data to Gemini.

```python
await gemini.send_audio(audio_data: bytes) -> None
```

## GeminiWebRTCBridge

Bridge between WebRTC session and Gemini API.

### Constructor

```python
GeminiWebRTCBridge(
    gemini: GeminiIntegration,
    session_config: SessionConfig
)
```

### Methods

#### start()

Start the bridge.

```python
await bridge.start() -> None
```

#### stop()

Stop the bridge.

```python
await bridge.stop() -> None
```

#### process_audio_frame(frame)

Process audio frame from WebRTC.

```python
await bridge.process_audio_frame(frame) -> None
```

#### process_text_message(message)

Process text message through Gemini.

```python
response = await bridge.process_text_message(message: str) -> str
```

**Example:**

```python
bridge = GeminiWebRTCBridge(gemini, session_config)
await bridge.start()

# Connect to session
session.on_audio_frame = bridge.process_audio_frame

# Process text
response = await bridge.process_text_message("Hello!")
```

## FastAPI Integration

### Basic Setup

```python
from fastapi import FastAPI, WebSocket
from webrtc_enterprise import WebRTCServer, GeminiIntegration

app = FastAPI()
server = WebRTCServer()
gemini = GeminiIntegration(api_key="your-key")

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await server.signaling.handle_connection(websocket)
```

### With Gemini Integration

```python
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    session_config = SessionConfig(
        session_id=str(uuid.uuid4()),
        use_gemini=True
    )

    session = await server.create_session(session_config)
    bridge = GeminiWebRTCBridge(gemini, session_config)
    await bridge.start()

    session.on_audio_frame = bridge.process_audio_frame

    await server.signaling.handle_connection(
        websocket,
        session_config
    )
```

## Types

### SessionConfig

```python
@dataclass
class SessionConfig:
    session_id: str
    use_gemini: bool = False
    gemini_model: str = "gemini-2.0-flash-exp"
    enable_audio: bool = True
    enable_video: bool = False
    enable_data_channel: bool = True
```

### MediaConfig

```python
@dataclass
class MediaConfig:
    audio_codec: str = "opus"
    video_codec: str = "VP8"
    audio_sample_rate: int = 48000
    audio_channels: int = 1
    video_width: int = 1280
    video_height: int = 720
```

### ConnectionState

```python
class ConnectionState(str, Enum):
    NEW = "new"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    CLOSED = "closed"
```
