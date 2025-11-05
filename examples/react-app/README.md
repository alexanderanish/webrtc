# WebRTC React Example Application

This is an example React application demonstrating the use of the `@webrtc-enterprise/client` library with Gemini real-time API integration.

## Features

- WebRTC connection management
- Audio streaming
- Text chat via data channels
- Real-time connection statistics
- Clean, responsive UI

## Prerequisites

- Node.js 18+ installed
- Backend server running on `http://localhost:8000`

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. Click "Connect" to establish WebSocket connection with the signaling server
2. Click "Start Audio" to begin streaming audio
3. Type messages in the chat to communicate with Gemini
4. Monitor connection statistics in real-time

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Environment Variables

You can create a `.env` file to configure:

```env
VITE_SIGNALING_URL=ws://localhost:8000/ws
```

## Architecture

```
App.tsx
├── useWebRTC - Main WebRTC connection
├── useMediaStream - Audio/video stream management
├── useDataChannel - Text messaging
└── useRemoteTracks - Remote media tracks
```
