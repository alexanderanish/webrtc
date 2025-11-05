/**
 * React Hooks for WebRTC Client
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { WebRTCClient } from './WebRTCClient';
import { RTCConfig, MediaConfig, DataMessage, ConnectionStats } from './types';

export interface UseWebRTCOptions extends RTCConfig {
  autoConnect?: boolean;
}

export interface UseWebRTCReturn {
  client: WebRTCClient | null;
  isConnected: boolean;
  connectionState: RTCPeerConnectionState;
  error: Error | null;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  sendData: (message: DataMessage) => Promise<void>;
  stats: ConnectionStats | null;
}

/**
 * Main hook for WebRTC functionality
 */
export function useWebRTC(options: UseWebRTCOptions): UseWebRTCReturn {
  const [client] = useState(() => new WebRTCClient(options));
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<RTCPeerConnectionState>('new');
  const [error, setError] = useState<Error | null>(null);
  const [stats, setStats] = useState<ConnectionStats | null>(null);

  const connect = useCallback(async () => {
    try {
      await client.connect();
    } catch (err) {
      setError(err as Error);
    }
  }, [client]);

  const disconnect = useCallback(async () => {
    await client.disconnect();
  }, [client]);

  const sendData = useCallback(
    async (message: DataMessage) => {
      try {
        await client.sendData(message);
      } catch (err) {
        setError(err as Error);
      }
    },
    [client]
  );

  useEffect(() => {
    const handleConnected = () => {
      setIsConnected(true);
      setError(null);
    };

    const handleDisconnected = () => {
      setIsConnected(false);
    };

    const handleError = (err: Error) => {
      setError(err);
    };

    const handleStateChange = (state: RTCPeerConnectionState) => {
      setConnectionState(state);
    };

    const handleStats = (newStats: ConnectionStats) => {
      setStats(newStats);
    };

    client.on('connected', handleConnected);
    client.on('disconnected', handleDisconnected);
    client.on('error', handleError);
    client.on('stateChange', handleStateChange);
    client.on('stats', handleStats);

    if (options.autoConnect) {
      connect();
    }

    return () => {
      client.off('connected', handleConnected);
      client.off('disconnected', handleDisconnected);
      client.off('error', handleError);
      client.off('stateChange', handleStateChange);
      client.off('stats', handleStats);
      disconnect();
    };
  }, [client, options.autoConnect, connect, disconnect]);

  return {
    client,
    isConnected,
    connectionState,
    error,
    connect,
    disconnect,
    sendData,
    stats,
  };
}

export interface UseMediaStreamReturn {
  stream: MediaStream | null;
  isStreaming: boolean;
  error: Error | null;
  startStream: (config?: MediaConfig) => Promise<void>;
  stopStream: () => void;
}

/**
 * Hook for managing media streams
 */
export function useMediaStream(client: WebRTCClient | null): UseMediaStreamReturn {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const startStream = useCallback(
    async (config: MediaConfig = { audio: true, video: false }) => {
      if (!client) {
        setError(new Error('Client not initialized'));
        return;
      }

      try {
        const mediaStream = await client.startMedia(config);
        setStream(mediaStream);
        setIsStreaming(true);
        setError(null);
      } catch (err) {
        setError(err as Error);
      }
    },
    [client]
  );

  const stopStream = useCallback(() => {
    if (client) {
      client.stopMedia();
      setStream(null);
      setIsStreaming(false);
    }
  }, [client]);

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);

  return {
    stream,
    isStreaming,
    error,
    startStream,
    stopStream,
  };
}

export interface UseDataChannelReturn {
  messages: DataMessage[];
  sendMessage: (message: DataMessage) => Promise<void>;
  clearMessages: () => void;
}

/**
 * Hook for managing data channel messages
 */
export function useDataChannel(client: WebRTCClient | null): UseDataChannelReturn {
  const [messages, setMessages] = useState<DataMessage[]>([]);

  const sendMessage = useCallback(
    async (message: DataMessage) => {
      if (!client) {
        throw new Error('Client not initialized');
      }
      await client.sendData(message);
    },
    [client]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  useEffect(() => {
    if (!client) return;

    const handleData = (message: DataMessage) => {
      setMessages((prev) => [...prev, message]);
    };

    client.on('data', handleData);

    return () => {
      client.off('data', handleData);
    };
  }, [client]);

  return {
    messages,
    sendMessage,
    clearMessages,
  };
}

export interface UseRemoteTracksReturn {
  tracks: MediaStreamTrack[];
  streams: MediaStream[];
}

/**
 * Hook for managing remote tracks
 */
export function useRemoteTracks(client: WebRTCClient | null): UseRemoteTracksReturn {
  const [tracks, setTracks] = useState<MediaStreamTrack[]>([]);
  const [streams, setStreams] = useState<MediaStream[]>([]);

  useEffect(() => {
    if (!client) return;

    const handleTrack = (track: MediaStreamTrack, stream: MediaStream) => {
      setTracks((prev) => [...prev, track]);
      setStreams((prev) => {
        if (!prev.find((s) => s.id === stream.id)) {
          return [...prev, stream];
        }
        return prev;
      });
    };

    client.on('track', handleTrack);

    return () => {
      client.off('track', handleTrack);
      setTracks([]);
      setStreams([]);
    };
  }, [client]);

  return { tracks, streams };
}
