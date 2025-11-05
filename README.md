# Enterprise WebRTC Library

A production-ready WebRTC library for building real-time communication applications with React and FastAPI, featuring seamless integration with Google's Gemini real-time API.

## Features

- 🎥 **Multi-modal Communication**: Audio, video, and data channels
- 🚀 **Enterprise-Ready**: TypeScript client library with full type safety
- 🐍 **Python Backend**: FastAPI-compatible server library with aiortc
- 🤖 **Gemini Integration**: Built-in support for Gemini real-time API
- 🔄 **Automatic Reconnection**: Robust error handling and recovery
- 📦 **Easy Integration**: Simple APIs for React and FastAPI
- 🔒 **Secure**: Support for TURN/STUN servers and encrypted connections
- 📊 **Monitoring**: Built-in stats and event tracking

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Client   │◄───────►│  FastAPI Server  │◄───────►│  Gemini API     │
│  (TypeScript)   │  WebRTC │  (Python)        │  GRPC   │  (Real-time)    │
│                 │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## Packages

### Client Library (`@webrtc-enterprise/client`)

TypeScript/JavaScript library for browser-based WebRTC applications.

**Key Features:**
- Peer connection management
- Media stream handling
- Data channel support
- Signaling client (WebSocket)
- Event-driven architecture
- React hooks

### Server Library (`webrtc-enterprise-server`)

Python library for building WebRTC servers with FastAPI.

**Key Features:**
- WebRTC server implementation (aiortc)
- Signaling server (WebSocket)
- Session management
- Gemini real-time API integration
- Media processing pipeline

## Quick Start

### Client (React)

```typescript
import { WebRTCClient } from '@webrtc-enterprise/client';

const client = new WebRTCClient({
  signalingUrl: 'ws://localhost:8000/ws',
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
});

// Send audio/video
await client.startMedia({ audio: true, video: true });

// Send text via data channel
await client.sendData({ type: 'text', content: 'Hello!' });

// Listen for responses
client.on('data', (data) => {
  console.log('Received:', data);
});
```

### Server (FastAPI)

```python
from fastapi import FastAPI, WebSocket
from webrtc_enterprise import WebRTCServer, GeminiIntegration

app = FastAPI()
webrtc_server = WebRTCServer()
gemini = GeminiIntegration(api_key="your-api-key")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await webrtc_server.handle_connection(websocket, gemini)
```

## Installation

```bash
# Client library
npm install @webrtc-enterprise/client

# Server library
pip install webrtc-enterprise-server
```

## Documentation

See the [docs](./docs) directory for detailed documentation:

- [Client API Reference](./docs/client-api.md)
- [Server API Reference](./docs/server-api.md)
- [Gemini Integration Guide](./docs/gemini-integration.md)
- [Deployment Guide](./docs/deployment.md)

## Examples

- [React Chat Application](./examples/react-app)
- [FastAPI Server](./examples/fastapi-server)

## Development

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Run tests
npm test
pytest

# Build
npm run build
python setup.py build
```

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.
