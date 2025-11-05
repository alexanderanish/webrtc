/**
 * WebRTC Enterprise Client Types
 */

export interface RTCConfig {
  signalingUrl: string;
  iceServers?: RTCIceServer[];
  reconnectAttempts?: number;
  reconnectDelay?: number;
  dataChannelLabel?: string;
}

export interface MediaConfig {
  audio?: boolean | MediaTrackConstraints;
  video?: boolean | MediaTrackConstraints;
}

export interface DataMessage {
  type: 'text' | 'binary' | 'json';
  content: any;
  timestamp?: number;
}

export interface SignalingMessage {
  type: 'offer' | 'answer' | 'ice-candidate' | 'error' | 'ready';
  data?: any;
  sessionId?: string;
}

export interface ConnectionStats {
  packetsLost: number;
  bytesReceived: number;
  bytesSent: number;
  currentRoundTripTime: number;
  availableOutgoingBitrate?: number;
}

export interface WebRTCClientEvents {
  connected: () => void;
  disconnected: () => void;
  error: (error: Error) => void;
  data: (message: DataMessage) => void;
  track: (track: MediaStreamTrack, stream: MediaStream) => void;
  stats: (stats: ConnectionStats) => void;
  stateChange: (state: RTCPeerConnectionState) => void;
}

export type EventHandler<T = any> = (data: T) => void;

export interface WebRTCClientInterface {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  startMedia(config: MediaConfig): Promise<MediaStream>;
  stopMedia(): void;
  sendData(message: DataMessage): Promise<void>;
  getStats(): Promise<ConnectionStats>;
  on<K extends keyof WebRTCClientEvents>(
    event: K,
    handler: WebRTCClientEvents[K]
  ): void;
  off<K extends keyof WebRTCClientEvents>(
    event: K,
    handler: WebRTCClientEvents[K]
  ): void;
}
