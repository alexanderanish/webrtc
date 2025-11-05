# Gemini Real-time API Integration Guide

This guide explains how to integrate Google's Gemini real-time API with your WebRTC application.

## Overview

The Gemini integration enables:
- Real-time audio streaming to/from Gemini
- Text-based conversation
- Multi-modal interactions
- Context-aware responses

## Setup

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Save it securely

### 2. Install Dependencies

```bash
pip install google-generativeai google-ai-generativelanguage
```

### 3. Configure Environment

```bash
export GEMINI_API_KEY="your-api-key"
export GEMINI_MODEL="gemini-2.0-flash-exp"
```

## Client-Side Integration

### React Component

```typescript
import { useWebRTC, useMediaStream, useDataChannel } from '@webrtc-enterprise/client';

function GeminiChat() {
  const { client, isConnected, connect } = useWebRTC({
    signalingUrl: 'ws://localhost:8000/ws',
    autoConnect: false
  });

  const { startStream } = useMediaStream(client);
  const { messages, sendMessage } = useDataChannel(client);

  const handleConnect = async () => {
    await connect();
    // Start audio streaming to Gemini
    await startStream({ audio: true, video: false });
  };

  const handleSendText = async (text: string) => {
    await sendMessage({
      type: 'text',
      content: text
    });
  };

  return (
    <div>
      <button onClick={handleConnect} disabled={isConnected}>
        Connect to Gemini
      </button>
      {messages.map((msg, idx) => (
        <div key={idx}>{msg.content}</div>
      ))}
    </div>
  );
}
```

## Server-Side Integration

### Basic Setup

```python
from fastapi import FastAPI, WebSocket
from webrtc_enterprise import (
    WebRTCServer,
    GeminiIntegration,
    GeminiWebRTCBridge,
    SessionConfig
)

app = FastAPI()
server = WebRTCServer()

# Initialize Gemini
gemini = GeminiIntegration(
    api_key="your-api-key",
    model_name="gemini-2.0-flash-exp",
    system_instruction="You are a helpful voice assistant."
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Create session with Gemini
    session_config = SessionConfig(
        session_id=str(uuid.uuid4()),
        use_gemini=True
    )

    session = await server.create_session(session_config)

    # Set up Gemini bridge
    bridge = GeminiWebRTCBridge(gemini, session_config)
    await bridge.start()

    # Connect audio pipeline
    session.on_audio_frame = bridge.process_audio_frame

    # Handle text messages
    async def handle_text(message: str):
        data = json.loads(message)
        if data['type'] == 'text':
            response = await bridge.process_text_message(data['content'])
            await session.send_data(json.dumps({
                'type': 'text',
                'content': response
            }))

    session.on_data_message = handle_text

    await server.signaling.handle_connection(websocket, session_config)
```

### Advanced Configuration

#### Custom System Instructions

```python
gemini = GeminiIntegration(
    api_key="your-api-key",
    system_instruction="""
    You are a technical support assistant specializing in WebRTC.
    Provide concise, helpful responses.
    Use technical terms when appropriate.
    Be friendly and professional.
    """
)
```

#### Audio Configuration

```python
media_config = MediaConfig(
    audio_codec="opus",
    audio_sample_rate=48000,  # Gemini prefers 48kHz
    audio_channels=1,         # Mono
)

server = WebRTCServer(media_config=media_config)
```

## Audio Streaming

### Client to Gemini

Audio flows: Microphone → WebRTC → Server → Gemini

```python
# Server automatically processes audio frames
session.on_audio_frame = bridge.process_audio_frame
```

### Gemini to Client

Audio flows: Gemini → Server → WebRTC → Speakers

```python
# Set up response handler
def on_gemini_audio(audio_chunk: bytes):
    # Send audio back to client
    # Implementation depends on your setup
    pass

bridge.set_audio_response_handler(on_gemini_audio)
```

## Text Messaging

### Send Text to Gemini

```typescript
// Client
await client.sendData({
  type: 'text',
  content: 'What is WebRTC?'
});
```

```python
# Server
response = await gemini.send_text("What is WebRTC?")
```

### Receive Responses

```typescript
// Client
client.on('data', (message) => {
  if (message.type === 'text') {
    console.log('Gemini:', message.content);
  }
});
```

## Error Handling

### Client-Side

```typescript
const { error } = useWebRTC(config);

useEffect(() => {
  if (error) {
    console.error('WebRTC Error:', error.message);
    // Show error to user
  }
}, [error]);
```

### Server-Side

```python
try:
    response = await gemini.send_text(text)
except Exception as e:
    logger.error(f"Gemini error: {e}")
    await session.send_data(json.dumps({
        'type': 'error',
        'content': 'Failed to process request'
    }))
```

## Best Practices

### 1. Audio Quality

- Use 48kHz sample rate for best quality
- Enable echo cancellation and noise suppression
- Use Opus codec for efficient transmission

```typescript
await startStream({
  audio: {
    sampleRate: 48000,
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
  }
});
```

### 2. Latency Optimization

- Use WebSocket for signaling (low overhead)
- Configure ICE servers close to users
- Use data channels for text (faster than audio)

### 3. Resource Management

- Close sessions when done
- Implement timeouts for inactive connections
- Clean up resources properly

```python
# Cleanup on disconnect
try:
    await server.signaling.handle_connection(websocket, session_config)
finally:
    await bridge.stop()
    await server.close_session(session_id)
```

### 4. Security

- Never expose API keys in client code
- Use environment variables
- Implement authentication
- Validate all inputs

```python
# Use environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set")
```

## Troubleshooting

### Common Issues

#### 1. No Audio Response

**Problem:** Audio sent but no response from Gemini

**Solutions:**
- Check API key is valid
- Verify audio format (16kHz PCM16 mono)
- Check Gemini API quotas
- Enable debug logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. High Latency

**Problem:** Slow responses from Gemini

**Solutions:**
- Use smaller audio chunks
- Implement audio buffering
- Check network connectivity
- Consider using text for simple queries

#### 3. Connection Drops

**Problem:** WebRTC connection unstable

**Solutions:**
- Configure TURN servers
- Implement reconnection logic
- Check firewall settings
- Monitor connection stats

```typescript
const stats = await client.getStats();
console.log('RTT:', stats.currentRoundTripTime);
```

## Example Use Cases

### 1. Voice Assistant

```python
gemini = GeminiIntegration(
    api_key=api_key,
    system_instruction="You are a voice assistant. Respond concisely."
)
```

### 2. Language Tutor

```python
gemini = GeminiIntegration(
    api_key=api_key,
    system_instruction="You are a language tutor. Help users practice speaking."
)
```

### 3. Customer Support

```python
gemini = GeminiIntegration(
    api_key=api_key,
    system_instruction="You are customer support for a tech company. Be helpful and professional."
)
```

## Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [WebRTC Specifications](https://webrtc.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## Next Steps

1. Implement authentication for production use
2. Add monitoring and analytics
3. Optimize audio processing pipeline
4. Implement fallback for API failures
5. Add support for multiple languages
