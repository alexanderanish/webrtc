/**
 * Enterprise-grade WebRTC Client
 * Handles peer connections, media streaming, and data channels
 */

import EventEmitter from 'eventemitter3';
import {
  RTCConfig,
  MediaConfig,
  DataMessage,
  SignalingMessage,
  ConnectionStats,
  WebRTCClientEvents,
  WebRTCClientInterface,
} from './types';

export class WebRTCClient extends EventEmitter<WebRTCClientEvents> implements WebRTCClientInterface {
  private config: Required<RTCConfig>;
  private peerConnection: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;
  private websocket: WebSocket | null = null;
  private localStream: MediaStream | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private reconnectCount = 0;
  private isConnecting = false;
  private sessionId: string | null = null;

  constructor(config: RTCConfig) {
    super();

    this.config = {
      signalingUrl: config.signalingUrl,
      iceServers: config.iceServers || [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
      ],
      reconnectAttempts: config.reconnectAttempts ?? 5,
      reconnectDelay: config.reconnectDelay ?? 2000,
      dataChannelLabel: config.dataChannelLabel || 'data',
    };
  }

  /**
   * Connect to the signaling server and establish WebRTC connection
   */
  async connect(): Promise<void> {
    if (this.isConnecting || this.websocket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;

    try {
      await this.connectWebSocket();
      await this.createPeerConnection();
      this.isConnecting = false;
    } catch (error) {
      this.isConnecting = false;
      throw error;
    }
  }

  /**
   * Disconnect and clean up resources
   */
  async disconnect(): Promise<void> {
    this.clearReconnectTimer();
    this.stopMedia();
    this.closeDataChannel();
    this.closePeerConnection();
    this.closeWebSocket();
    this.sessionId = null;
    this.emit('disconnected');
  }

  /**
   * Start capturing local media (audio/video)
   */
  async startMedia(config: MediaConfig): Promise<MediaStream> {
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia({
        audio: config.audio ?? true,
        video: config.video ?? false,
      });

      if (this.peerConnection) {
        this.localStream.getTracks().forEach((track) => {
          this.peerConnection!.addTrack(track, this.localStream!);
        });

        // Renegotiate after adding tracks
        await this.createAndSendOffer();
      }

      return this.localStream;
    } catch (error) {
      const err = new Error(`Failed to access media devices: ${error}`);
      this.emit('error', err);
      throw err;
    }
  }

  /**
   * Stop local media streams
   */
  stopMedia(): void {
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
  }

  /**
   * Send data through the data channel
   */
  async sendData(message: DataMessage): Promise<void> {
    if (!this.dataChannel || this.dataChannel.readyState !== 'open') {
      throw new Error('Data channel is not open');
    }

    const payload = {
      ...message,
      timestamp: message.timestamp || Date.now(),
    };

    try {
      if (message.type === 'binary') {
        this.dataChannel.send(payload.content);
      } else {
        this.dataChannel.send(JSON.stringify(payload));
      }
    } catch (error) {
      const err = new Error(`Failed to send data: ${error}`);
      this.emit('error', err);
      throw err;
    }
  }

  /**
   * Get connection statistics
   */
  async getStats(): Promise<ConnectionStats> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not established');
    }

    const stats = await this.peerConnection.getStats();
    const result: ConnectionStats = {
      packetsLost: 0,
      bytesReceived: 0,
      bytesSent: 0,
      currentRoundTripTime: 0,
    };

    stats.forEach((report) => {
      if (report.type === 'inbound-rtp') {
        result.packetsLost += report.packetsLost || 0;
        result.bytesReceived += report.bytesReceived || 0;
      } else if (report.type === 'outbound-rtp') {
        result.bytesSent += report.bytesSent || 0;
      } else if (report.type === 'candidate-pair' && report.state === 'succeeded') {
        result.currentRoundTripTime = report.currentRoundTripTime || 0;
        result.availableOutgoingBitrate = report.availableOutgoingBitrate;
      }
    });

    return result;
  }

  // Private methods

  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.websocket = new WebSocket(this.config.signalingUrl);

        this.websocket.onopen = () => {
          this.reconnectCount = 0;
          resolve();
        };

        this.websocket.onmessage = (event) => {
          this.handleSignalingMessage(JSON.parse(event.data));
        };

        this.websocket.onerror = (error) => {
          reject(new Error('WebSocket connection failed'));
        };

        this.websocket.onclose = () => {
          this.handleWebSocketClose();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private closeWebSocket(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  private handleWebSocketClose(): void {
    this.emit('disconnected');

    if (this.reconnectCount < this.config.reconnectAttempts) {
      this.scheduleReconnect();
    } else {
      this.emit('error', new Error('Max reconnection attempts reached'));
    }
  }

  private scheduleReconnect(): void {
    this.clearReconnectTimer();
    this.reconnectCount++;

    const delay = this.config.reconnectDelay * this.reconnectCount;
    this.reconnectTimer = setTimeout(() => {
      this.connect().catch((error) => {
        this.emit('error', new Error(`Reconnection failed: ${error}`));
      });
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private async createPeerConnection(): Promise<void> {
    this.peerConnection = new RTCPeerConnection({
      iceServers: this.config.iceServers,
    });

    // Set up event handlers
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        this.sendSignalingMessage({
          type: 'ice-candidate',
          data: event.candidate,
          sessionId: this.sessionId || undefined,
        });
      }
    };

    this.peerConnection.ontrack = (event) => {
      this.emit('track', event.track, event.streams[0]);
    };

    this.peerConnection.onconnectionstatechange = () => {
      const state = this.peerConnection!.connectionState;
      this.emit('stateChange', state);

      if (state === 'connected') {
        this.emit('connected');
      } else if (state === 'failed' || state === 'closed') {
        this.handleConnectionFailure();
      }
    };

    this.peerConnection.ondatachannel = (event) => {
      this.setupDataChannel(event.channel);
    };

    // Create data channel
    this.dataChannel = this.peerConnection.createDataChannel(
      this.config.dataChannelLabel
    );
    this.setupDataChannel(this.dataChannel);
  }

  private setupDataChannel(channel: RTCDataChannel): void {
    this.dataChannel = channel;

    this.dataChannel.onopen = () => {
      console.log('Data channel opened');
    };

    this.dataChannel.onmessage = (event) => {
      try {
        const message: DataMessage = typeof event.data === 'string'
          ? JSON.parse(event.data)
          : { type: 'binary', content: event.data, timestamp: Date.now() };

        this.emit('data', message);
      } catch (error) {
        this.emit('error', new Error(`Failed to parse data message: ${error}`));
      }
    };

    this.dataChannel.onerror = (error) => {
      this.emit('error', new Error('Data channel error'));
    };
  }

  private closeDataChannel(): void {
    if (this.dataChannel) {
      this.dataChannel.close();
      this.dataChannel = null;
    }
  }

  private closePeerConnection(): void {
    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }
  }

  private async handleSignalingMessage(message: SignalingMessage): Promise<void> {
    try {
      switch (message.type) {
        case 'ready':
          this.sessionId = message.sessionId || null;
          await this.createAndSendOffer();
          break;

        case 'answer':
          if (this.peerConnection && message.data) {
            await this.peerConnection.setRemoteDescription(
              new RTCSessionDescription(message.data)
            );
          }
          break;

        case 'ice-candidate':
          if (this.peerConnection && message.data) {
            await this.peerConnection.addIceCandidate(
              new RTCIceCandidate(message.data)
            );
          }
          break;

        case 'error':
          this.emit('error', new Error(message.data?.message || 'Signaling error'));
          break;
      }
    } catch (error) {
      this.emit('error', new Error(`Failed to handle signaling message: ${error}`));
    }
  }

  private async createAndSendOffer(): Promise<void> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not established');
    }

    const offer = await this.peerConnection.createOffer();
    await this.peerConnection.setLocalDescription(offer);

    this.sendSignalingMessage({
      type: 'offer',
      data: offer,
      sessionId: this.sessionId || undefined,
    });
  }

  private sendSignalingMessage(message: SignalingMessage): void {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    }
  }

  private handleConnectionFailure(): void {
    this.emit('error', new Error('Peer connection failed'));

    if (this.reconnectCount < this.config.reconnectAttempts) {
      this.disconnect().then(() => {
        this.scheduleReconnect();
      });
    }
  }
}
