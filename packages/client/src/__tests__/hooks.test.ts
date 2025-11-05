/**
 * Tests for React hooks
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useWebRTC, useMediaStream, useDataChannel, useRemoteTracks } from '../hooks';
import { WebRTCClient } from '../WebRTCClient';

jest.mock('../WebRTCClient');

describe('React Hooks', () => {
  let mockClient: jest.Mocked<WebRTCClient>;

  beforeEach(() => {
    jest.clearAllMocks();

    mockClient = {
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      startMedia: jest.fn().mockResolvedValue({
        getTracks: () => [],
      } as any),
      stopMedia: jest.fn(),
      sendData: jest.fn().mockResolvedValue(undefined),
      getStats: jest.fn().mockResolvedValue({
        packetsLost: 0,
        bytesReceived: 1000,
        bytesSent: 2000,
        currentRoundTripTime: 0.05,
      }),
      on: jest.fn(),
      off: jest.fn(),
      emit: jest.fn(),
    } as any;

    (WebRTCClient as jest.Mock).mockImplementation(() => mockClient);
  });

  describe('useWebRTC', () => {
    it('should initialize client', () => {
      const { result } = renderHook(() =>
        useWebRTC({
          signalingUrl: 'ws://localhost:8000/ws',
        })
      );

      expect(result.current.client).toBe(mockClient);
      expect(result.current.isConnected).toBe(false);
    });

    it('should auto-connect when autoConnect is true', async () => {
      renderHook(() =>
        useWebRTC({
          signalingUrl: 'ws://localhost:8000/ws',
          autoConnect: true,
        })
      );

      await waitFor(() => {
        expect(mockClient.connect).toHaveBeenCalled();
      });
    });

    it('should connect manually', async () => {
      const { result } = renderHook(() =>
        useWebRTC({
          signalingUrl: 'ws://localhost:8000/ws',
          autoConnect: false,
        })
      );

      await act(async () => {
        await result.current.connect();
      });

      expect(mockClient.connect).toHaveBeenCalled();
    });

    it('should disconnect', async () => {
      const { result } = renderHook(() =>
        useWebRTC({
          signalingUrl: 'ws://localhost:8000/ws',
        })
      );

      await act(async () => {
        await result.current.disconnect();
      });

      expect(mockClient.disconnect).toHaveBeenCalled();
    });

    it('should update connection state', async () => {
      const { result } = renderHook(() =>
        useWebRTC({
          signalingUrl: 'ws://localhost:8000/ws',
        })
      );

      // Simulate connected event
      const connectedHandler = (mockClient.on as jest.Mock).mock.calls.find(
        (call) => call[0] === 'connected'
      )?.[1];

      act(() => {
        if (connectedHandler) connectedHandler();
      });

      await waitFor(() => {
        expect(result.current.isConnected).toBe(true);
      });
    });

    it('should handle errors', async () => {
      const { result } = renderHook(() =>
        useWebRTC({
          signalingUrl: 'ws://localhost:8000/ws',
        })
      );

      const error = new Error('Connection failed');
      const errorHandler = (mockClient.on as jest.Mock).mock.calls.find(
        (call) => call[0] === 'error'
      )?.[1];

      act(() => {
        if (errorHandler) errorHandler(error);
      });

      await waitFor(() => {
        expect(result.current.error).toBe(error);
      });
    });

    it('should cleanup on unmount', () => {
      const { unmount } = renderHook(() =>
        useWebRTC({
          signalingUrl: 'ws://localhost:8000/ws',
        })
      );

      unmount();

      expect(mockClient.disconnect).toHaveBeenCalled();
    });
  });

  describe('useMediaStream', () => {
    it('should start media stream', async () => {
      const { result } = renderHook(() => useMediaStream(mockClient));

      await act(async () => {
        await result.current.startStream({ audio: true, video: false });
      });

      expect(mockClient.startMedia).toHaveBeenCalledWith({
        audio: true,
        video: false,
      });
      expect(result.current.isStreaming).toBe(true);
    });

    it('should stop media stream', async () => {
      const { result } = renderHook(() => useMediaStream(mockClient));

      await act(async () => {
        await result.current.startStream({ audio: true });
      });

      act(() => {
        result.current.stopStream();
      });

      expect(mockClient.stopMedia).toHaveBeenCalled();
      expect(result.current.isStreaming).toBe(false);
    });

    it('should handle errors', async () => {
      mockClient.startMedia.mockRejectedValueOnce(new Error('Permission denied'));

      const { result } = renderHook(() => useMediaStream(mockClient));

      await act(async () => {
        await result.current.startStream({ audio: true });
      });

      expect(result.current.error).toBeDefined();
      expect(result.current.error?.message).toBe('Permission denied');
    });

    it('should return error if client not initialized', async () => {
      const { result } = renderHook(() => useMediaStream(null));

      await act(async () => {
        await result.current.startStream({ audio: true });
      });

      expect(result.current.error?.message).toBe('Client not initialized');
    });

    it('should cleanup on unmount', () => {
      const { unmount } = renderHook(() => useMediaStream(mockClient));

      unmount();

      expect(mockClient.stopMedia).toHaveBeenCalled();
    });
  });

  describe('useDataChannel', () => {
    it('should send message', async () => {
      const { result } = renderHook(() => useDataChannel(mockClient));

      const message = { type: 'text' as const, content: 'Hello' };

      await act(async () => {
        await result.current.sendMessage(message);
      });

      expect(mockClient.sendData).toHaveBeenCalledWith(message);
    });

    it('should receive messages', async () => {
      const { result } = renderHook(() => useDataChannel(mockClient));

      const message = { type: 'text' as const, content: 'Hello', timestamp: Date.now() };
      const dataHandler = (mockClient.on as jest.Mock).mock.calls.find(
        (call) => call[0] === 'data'
      )?.[1];

      act(() => {
        if (dataHandler) dataHandler(message);
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0]).toEqual(message);
      });
    });

    it('should clear messages', async () => {
      const { result } = renderHook(() => useDataChannel(mockClient));

      const message = { type: 'text' as const, content: 'Hello', timestamp: Date.now() };
      const dataHandler = (mockClient.on as jest.Mock).mock.calls.find(
        (call) => call[0] === 'data'
      )?.[1];

      act(() => {
        if (dataHandler) dataHandler(message);
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
      });

      act(() => {
        result.current.clearMessages();
      });

      expect(result.current.messages).toHaveLength(0);
    });

    it('should throw error if client not initialized', async () => {
      const { result } = renderHook(() => useDataChannel(null));

      await expect(
        result.current.sendMessage({ type: 'text', content: 'Test' })
      ).rejects.toThrow('Client not initialized');
    });
  });

  describe('useRemoteTracks', () => {
    it('should track remote media tracks', async () => {
      const { result } = renderHook(() => useRemoteTracks(mockClient));

      const mockTrack = { kind: 'audio' } as MediaStreamTrack;
      const mockStream = { id: 'stream1' } as MediaStream;

      const trackHandler = (mockClient.on as jest.Mock).mock.calls.find(
        (call) => call[0] === 'track'
      )?.[1];

      act(() => {
        if (trackHandler) trackHandler(mockTrack, mockStream);
      });

      await waitFor(() => {
        expect(result.current.tracks).toHaveLength(1);
        expect(result.current.tracks[0]).toBe(mockTrack);
        expect(result.current.streams).toHaveLength(1);
        expect(result.current.streams[0]).toBe(mockStream);
      });
    });

    it('should not duplicate streams', async () => {
      const { result } = renderHook(() => useRemoteTracks(mockClient));

      const mockTrack1 = { kind: 'audio' } as MediaStreamTrack;
      const mockTrack2 = { kind: 'video' } as MediaStreamTrack;
      const mockStream = { id: 'stream1' } as MediaStream;

      const trackHandler = (mockClient.on as jest.Mock).mock.calls.find(
        (call) => call[0] === 'track'
      )?.[1];

      act(() => {
        if (trackHandler) {
          trackHandler(mockTrack1, mockStream);
          trackHandler(mockTrack2, mockStream); // Same stream
        }
      });

      await waitFor(() => {
        expect(result.current.tracks).toHaveLength(2);
        expect(result.current.streams).toHaveLength(1); // Should not duplicate
      });
    });

    it('should cleanup on unmount', () => {
      const { unmount } = renderHook(() => useRemoteTracks(mockClient));

      unmount();

      // Should clean up event listeners
      expect(mockClient.off).toHaveBeenCalled();
    });
  });
});
