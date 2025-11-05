# Client API Reference

## WebRTCClient

The main class for managing WebRTC connections.

### Constructor

```typescript
new WebRTCClient(config: RTCConfig)
```

**Parameters:**

- `config.signalingUrl` (string, required): WebSocket signaling server URL
- `config.iceServers` (RTCIceServer[], optional): Array of ICE servers (STUN/TURN)
- `config.reconnectAttempts` (number, optional): Max reconnection attempts (default: 5)
- `config.reconnectDelay` (number, optional): Reconnection delay in ms (default: 2000)
- `config.dataChannelLabel` (string, optional): Data channel label (default: 'data')

**Example:**

```typescript
const client = new WebRTCClient({
  signalingUrl: 'ws://localhost:8000/ws',
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' }
  ],
  reconnectAttempts: 3,
  reconnectDelay: 1000
});
```

### Methods

#### connect()

Establish connection to signaling server and create peer connection.

```typescript
await client.connect(): Promise<void>
```

#### disconnect()

Disconnect and clean up all resources.

```typescript
await client.disconnect(): Promise<void>
```

#### startMedia(config)

Start capturing local media (audio/video).

```typescript
await client.startMedia(config: MediaConfig): Promise<MediaStream>
```

**Parameters:**

- `config.audio` (boolean | MediaTrackConstraints): Enable/configure audio
- `config.video` (boolean | MediaTrackConstraints): Enable/configure video

**Example:**

```typescript
const stream = await client.startMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    sampleRate: 48000
  },
  video: false
});
```

#### stopMedia()

Stop all local media streams.

```typescript
client.stopMedia(): void
```

#### sendData(message)

Send data through the data channel.

```typescript
await client.sendData(message: DataMessage): Promise<void>
```

**Parameters:**

- `message.type` ('text' | 'binary' | 'json'): Message type
- `message.content` (any): Message content
- `message.timestamp` (number, optional): Unix timestamp

**Example:**

```typescript
await client.sendData({
  type: 'text',
  content: 'Hello, world!'
});
```

#### getStats()

Get connection statistics.

```typescript
await client.getStats(): Promise<ConnectionStats>
```

**Returns:**

```typescript
{
  packetsLost: number;
  bytesReceived: number;
  bytesSent: number;
  currentRoundTripTime: number;
  availableOutgoingBitrate?: number;
}
```

### Events

Listen to events using `on()` and `off()` methods.

#### connected

Emitted when peer connection is established.

```typescript
client.on('connected', () => {
  console.log('Connected!');
});
```

#### disconnected

Emitted when connection is closed.

```typescript
client.on('disconnected', () => {
  console.log('Disconnected');
});
```

#### error

Emitted when an error occurs.

```typescript
client.on('error', (error: Error) => {
  console.error('Error:', error.message);
});
```

#### data

Emitted when data is received through data channel.

```typescript
client.on('data', (message: DataMessage) => {
  console.log('Received:', message.content);
});
```

#### track

Emitted when remote track is received.

```typescript
client.on('track', (track: MediaStreamTrack, stream: MediaStream) => {
  console.log('Received track:', track.kind);
});
```

#### stateChange

Emitted when connection state changes.

```typescript
client.on('stateChange', (state: RTCPeerConnectionState) => {
  console.log('State:', state);
});
```

#### stats

Emitted periodically with connection statistics.

```typescript
client.on('stats', (stats: ConnectionStats) => {
  console.log('RTT:', stats.currentRoundTripTime);
});
```

## React Hooks

### useWebRTC

Main hook for WebRTC functionality.

```typescript
const {
  client,
  isConnected,
  connectionState,
  error,
  connect,
  disconnect,
  sendData,
  stats
} = useWebRTC(options: UseWebRTCOptions);
```

**Options:**

- All `RTCConfig` options
- `autoConnect` (boolean, optional): Auto-connect on mount

**Example:**

```typescript
const { client, isConnected, connect } = useWebRTC({
  signalingUrl: 'ws://localhost:8000/ws',
  autoConnect: true
});
```

### useMediaStream

Hook for managing media streams.

```typescript
const {
  stream,
  isStreaming,
  error,
  startStream,
  stopStream
} = useMediaStream(client);
```

**Example:**

```typescript
const { stream, startStream, stopStream } = useMediaStream(client);

// Start audio
await startStream({ audio: true, video: false });

// Stop streaming
stopStream();
```

### useDataChannel

Hook for managing data channel messages.

```typescript
const {
  messages,
  sendMessage,
  clearMessages
} = useDataChannel(client);
```

**Example:**

```typescript
const { messages, sendMessage } = useDataChannel(client);

await sendMessage({
  type: 'text',
  content: 'Hello!'
});
```

### useRemoteTracks

Hook for managing remote media tracks.

```typescript
const {
  tracks,
  streams
} = useRemoteTracks(client);
```

**Example:**

```typescript
const { streams } = useRemoteTracks(client);

useEffect(() => {
  if (audioRef.current && streams[0]) {
    audioRef.current.srcObject = streams[0];
  }
}, [streams]);
```

## Types

### RTCConfig

```typescript
interface RTCConfig {
  signalingUrl: string;
  iceServers?: RTCIceServer[];
  reconnectAttempts?: number;
  reconnectDelay?: number;
  dataChannelLabel?: string;
}
```

### MediaConfig

```typescript
interface MediaConfig {
  audio?: boolean | MediaTrackConstraints;
  video?: boolean | MediaTrackConstraints;
}
```

### DataMessage

```typescript
interface DataMessage {
  type: 'text' | 'binary' | 'json';
  content: any;
  timestamp?: number;
}
```

### ConnectionStats

```typescript
interface ConnectionStats {
  packetsLost: number;
  bytesReceived: number;
  bytesSent: number;
  currentRoundTripTime: number;
  availableOutgoingBitrate?: number;
}
```
