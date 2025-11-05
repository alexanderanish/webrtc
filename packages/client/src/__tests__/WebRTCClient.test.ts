/**
 * Tests for WebRTCClient
 */

import { WebRTCClient } from '../WebRTCClient';
import { RTCConfig, DataMessage } from '../types';

describe('WebRTCClient', () => {
  let client: WebRTCClient;
  let mockWebSocket: any;
  let mockPeerConnection: any;

  const defaultConfig: RTCConfig = {
    signalingUrl: 'ws://localhost:8000/ws',
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
  };

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock WebSocket instance
    mockWebSocket = {
      send: jest.fn(),
      close: jest.fn(),
      readyState: 1,
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as jest.Mock).mockReturnValue(mockWebSocket);

    // Mock RTCPeerConnection instance
    mockPeerConnection = {
      createOffer: jest.fn().mockResolvedValue({ sdp: 'offer', type: 'offer' }),
      createAnswer: jest.fn().mockResolvedValue({ sdp: 'answer', type: 'answer' }),
      setLocalDescription: jest.fn().mockResolvedValue(undefined),
      setRemoteDescription: jest.fn().mockResolvedValue(undefined),
      addIceCandidate: jest.fn().mockResolvedValue(undefined),
      addTrack: jest.fn(),
      close: jest.fn(),
      getStats: jest.fn().mockResolvedValue(new Map()),
      createDataChannel: jest.fn(() => ({
        send: jest.fn(),
        close: jest.fn(),
        readyState: 'open',
        onopen: null,
        onmessage: null,
        onerror: null,
      })),
      onicecandidate: null,
      ontrack: null,
      onconnectionstatechange: null,
      ondatachannel: null,
      connectionState: 'new',
      localDescription: { sdp: 'offer', type: 'offer' },
    };

    (global.RTCPeerConnection as jest.Mock).mockReturnValue(mockPeerConnection);

    client = new WebRTCClient(defaultConfig);
  });

  afterEach(async () => {
    await client.disconnect();
  });

  describe('Constructor', () => {
    it('should create client with default config', () => {
      expect(client).toBeInstanceOf(WebRTCClient);
    });

    it('should use custom reconnect settings', () => {
      const customClient = new WebRTCClient({
        ...defaultConfig,
        reconnectAttempts: 10,
        reconnectDelay: 5000,
      });
      expect(customClient).toBeInstanceOf(WebRTCClient);
    });
  });

  describe('connect()', () => {
    it('should establish WebSocket connection', async () => {
      const connectPromise = client.connect();

      // Simulate WebSocket open
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }

      await connectPromise;

      expect(WebSocket).toHaveBeenCalledWith(defaultConfig.signalingUrl);
      expect(RTCPeerConnection).toHaveBeenCalled();
    });

    it('should not connect twice if already connecting', async () => {
      const promise1 = client.connect();

      // Simulate WebSocket open
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }

      await promise1;

      await client.connect(); // Second call should be no-op

      expect(WebSocket).toHaveBeenCalledTimes(1);
    });

    it('should handle connection errors', async () => {
      const connectPromise = client.connect();

      // Simulate WebSocket error
      if (mockWebSocket.onerror) {
        mockWebSocket.onerror(new Event('error'));
      }

      await expect(connectPromise).rejects.toThrow();
    });
  });

  describe('disconnect()', () => {
    beforeEach(async () => {
      const connectPromise = client.connect();
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }
      await connectPromise;
    });

    it('should close WebSocket and peer connection', async () => {
      await client.disconnect();

      expect(mockWebSocket.close).toHaveBeenCalled();
      expect(mockPeerConnection.close).toHaveBeenCalled();
    });

    it('should emit disconnected event', async () => {
      const disconnectedHandler = jest.fn();
      client.on('disconnected', disconnectedHandler);

      await client.disconnect();

      expect(disconnectedHandler).toHaveBeenCalled();
    });
  });

  describe('startMedia()', () => {
    beforeEach(async () => {
      const connectPromise = client.connect();
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }
      await connectPromise;
    });

    it('should start audio stream', async () => {
      const stream = await client.startMedia({ audio: true, video: false });

      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        audio: true,
        video: false,
      });
      expect(stream).toBeDefined();
    });

    it('should add tracks to peer connection', async () => {
      await client.startMedia({ audio: true, video: false });

      expect(mockPeerConnection.addTrack).toHaveBeenCalled();
    });

    it('should handle media device errors', async () => {
      (navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValueOnce(
        new Error('Permission denied')
      );

      const errorHandler = jest.fn();
      client.on('error', errorHandler);

      await expect(
        client.startMedia({ audio: true, video: false })
      ).rejects.toThrow();
      expect(errorHandler).toHaveBeenCalled();
    });
  });

  describe('stopMedia()', () => {
    it('should stop all media tracks', async () => {
      const connectPromise = client.connect();
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }
      await connectPromise;

      const mockTrack = { stop: jest.fn(), kind: 'audio' };
      (navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValueOnce({
        getTracks: jest.fn(() => [mockTrack]),
      });

      await client.startMedia({ audio: true });
      client.stopMedia();

      expect(mockTrack.stop).toHaveBeenCalled();
    });
  });

  describe('sendData()', () => {
    let mockDataChannel: any;

    beforeEach(async () => {
      mockDataChannel = {
        send: jest.fn(),
        close: jest.fn(),
        readyState: 'open',
      };

      mockPeerConnection.createDataChannel.mockReturnValue(mockDataChannel);

      const connectPromise = client.connect();
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }
      await connectPromise;
    });

    it('should send text message', async () => {
      const message: DataMessage = {
        type: 'text',
        content: 'Hello, world!',
      };

      await client.sendData(message);

      expect(mockDataChannel.send).toHaveBeenCalled();
      const sentData = JSON.parse(mockDataChannel.send.mock.calls[0][0]);
      expect(sentData.content).toBe('Hello, world!');
    });

    it('should send binary message', async () => {
      const message: DataMessage = {
        type: 'binary',
        content: new Uint8Array([1, 2, 3]),
      };

      await client.sendData(message);

      expect(mockDataChannel.send).toHaveBeenCalledWith(message.content);
    });

    it('should add timestamp if not provided', async () => {
      const message: DataMessage = {
        type: 'text',
        content: 'Test',
      };

      await client.sendData(message);

      const sentData = JSON.parse(mockDataChannel.send.mock.calls[0][0]);
      expect(sentData.timestamp).toBeDefined();
    });

    it('should throw error if data channel not open', async () => {
      mockDataChannel.readyState = 'closed';

      await expect(
        client.sendData({ type: 'text', content: 'Test' })
      ).rejects.toThrow('Data channel is not open');
    });
  });

  describe('getStats()', () => {
    beforeEach(async () => {
      const connectPromise = client.connect();
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }
      await connectPromise;
    });

    it('should return connection statistics', async () => {
      const mockStats = new Map([
        [
          'inbound-rtp',
          {
            type: 'inbound-rtp',
            packetsLost: 10,
            bytesReceived: 1000,
          },
        ],
        [
          'outbound-rtp',
          {
            type: 'outbound-rtp',
            bytesSent: 2000,
          },
        ],
        [
          'candidate-pair',
          {
            type: 'candidate-pair',
            state: 'succeeded',
            currentRoundTripTime: 0.05,
          },
        ],
      ]);

      mockPeerConnection.getStats.mockResolvedValue(mockStats);

      const stats = await client.getStats();

      expect(stats.packetsLost).toBe(10);
      expect(stats.bytesReceived).toBe(1000);
      expect(stats.bytesSent).toBe(2000);
      expect(stats.currentRoundTripTime).toBe(0.05);
    });

    it('should throw error if not connected', async () => {
      const newClient = new WebRTCClient(defaultConfig);

      await expect(newClient.getStats()).rejects.toThrow(
        'Peer connection not established'
      );
    });
  });

  describe('Event handling', () => {
    it('should emit connected event', async () => {
      const connectedHandler = jest.fn();
      client.on('connected', connectedHandler);

      const connectPromise = client.connect();
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }
      await connectPromise;

      // Simulate connection state change
      mockPeerConnection.connectionState = 'connected';
      if (mockPeerConnection.onconnectionstatechange) {
        mockPeerConnection.onconnectionstatechange();
      }

      expect(connectedHandler).toHaveBeenCalled();
    });

    it('should emit error event', () => {
      const errorHandler = jest.fn();
      client.on('error', errorHandler);

      const error = new Error('Test error');
      client.emit('error', error);

      expect(errorHandler).toHaveBeenCalledWith(error);
    });

    it('should remove event listeners with off()', () => {
      const handler = jest.fn();
      client.on('connected', handler);
      client.off('connected', handler);

      client.emit('connected');

      expect(handler).not.toHaveBeenCalled();
    });
  });

  describe('Reconnection', () => {
    beforeEach(async () => {
      client = new WebRTCClient({
        ...defaultConfig,
        reconnectAttempts: 3,
        reconnectDelay: 100,
      });

      const connectPromise = client.connect();
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen();
      }
      await connectPromise;
    });

    it('should attempt reconnection on disconnect', (done) => {
      jest.useFakeTimers();

      // Simulate WebSocket close
      if (mockWebSocket.onclose) {
        mockWebSocket.onclose();
      }

      // Fast-forward time
      jest.advanceTimersByTime(150);

      // Should attempt to reconnect
      expect(WebSocket).toHaveBeenCalledTimes(2);

      jest.useRealTimers();
      done();
    });
  });
});
