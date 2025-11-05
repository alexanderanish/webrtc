# FastAPI WebRTC Server Example

This is an example FastAPI server demonstrating the use of the `webrtc-enterprise-server` library with Google Gemini real-time API integration.

## Features

- WebRTC signaling server
- Audio/video stream processing
- Data channel support
- Google Gemini real-time API integration
- Session management
- Health check endpoints
- CORS configuration

## Prerequisites

- Python 3.9+ installed
- Google Gemini API key

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development, install the local package
pip install -e ../../packages/server
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
HOST=0.0.0.0
PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

## Running the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check

```bash
GET /
GET /health
```

Returns server status and configuration.

### WebSocket Signaling

```bash
WS /ws
```

WebSocket endpoint for WebRTC signaling. Clients connect here to establish WebRTC connections.

### Session Management

```bash
GET /sessions
```

Returns list of active WebRTC sessions.

## Usage with React Client

1. Start the FastAPI server:
   ```bash
   python main.py
   ```

2. Start the React client:
   ```bash
   cd ../react-app
   npm run dev
   ```

3. Open `http://localhost:3000` in your browser

4. Click "Connect" to establish WebSocket connection

5. Click "Start Audio" to begin streaming

6. Type messages to interact with Gemini

## Architecture

```
FastAPI Server
├── WebSocket Signaling (/ws)
├── WebRTC Server (aiortc)
├── Session Management
├── Gemini Integration
└── Media Processing Pipeline
```

## Troubleshooting

### Port Already in Use

Change the PORT in `.env`:

```env
PORT=8001
```

### CORS Errors

Add your frontend URL to ALLOWED_ORIGINS in `.env`:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Gemini API Errors

Verify your API key is correct and has access to the Gemini API:

```bash
# Test API key
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"
```

## Production Deployment

For production, consider:

1. Use a production ASGI server (uvicorn with multiple workers)
2. Set up HTTPS/WSS with proper certificates
3. Configure TURN servers for NAT traversal
4. Implement rate limiting
5. Add authentication/authorization
6. Monitor with logging and metrics
7. Use environment-specific configurations

Example production command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

## License

MIT
