import React, { useState, useEffect, useRef } from 'react';
import {
  useWebRTC,
  useMediaStream,
  useDataChannel,
  useRemoteTracks,
  GeminiConfig,
} from '@webrtc-enterprise/client';
import { GeminiConfigPanel } from './GeminiConfig';

const SIGNALING_URL = 'ws://localhost:8000/ws';

function App() {
  const [messageInput, setMessageInput] = useState('');

  const {
    client,
    isConnected,
    connectionState,
    error,
    connect,
    disconnect,
    stats,
  } = useWebRTC({
    signalingUrl: SIGNALING_URL,
    autoConnect: false,
  });

  const { stream, isStreaming, startStream, stopStream } = useMediaStream(client);
  const { messages, sendMessage, clearMessages } = useDataChannel(client);
  const { streams: remoteStreams } = useRemoteTracks(client);

  const localAudioRef = useRef<HTMLAudioElement>(null);
  const remoteAudioRef = useRef<HTMLAudioElement>(null);

  // Update local audio element when stream changes
  useEffect(() => {
    if (localAudioRef.current && stream) {
      localAudioRef.current.srcObject = stream;
    }
  }, [stream]);

  // Update remote audio element when remote streams change
  useEffect(() => {
    if (remoteAudioRef.current && remoteStreams.length > 0) {
      remoteAudioRef.current.srcObject = remoteStreams[0];
    }
  }, [remoteStreams]);

  const handleConnect = async () => {
    try {
      await connect();
    } catch (err) {
      console.error('Failed to connect:', err);
    }
  };

  const handleDisconnect = async () => {
    stopStream();
    await disconnect();
  };

  const handleStartAudio = async () => {
    try {
      await startStream({ audio: true, video: false });
    } catch (err) {
      console.error('Failed to start audio:', err);
    }
  };

  const handleSendMessage = async () => {
    if (!messageInput.trim()) return;

    try {
      await sendMessage({
        type: 'text',
        content: messageInput,
      });
      setMessageInput('');
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleApplyGeminiConfig = async (config: GeminiConfig) => {
    if (!client) {
      console.error('Client not initialized');
      return;
    }

    try {
      await client.sendGeminiConfig(config);
      console.log('Gemini configuration sent:', config);
      alert('Gemini configuration applied successfully!');
    } catch (err) {
      console.error('Failed to send Gemini config:', err);
      alert('Failed to apply Gemini configuration. Make sure you are connected.');
    }
  };

  return (
    <div className="app">
      <h1>WebRTC Enterprise - React Example</h1>

      <div className="container">
        {/* Status Bar */}
        <div className="status-bar">
          <div className="status-indicator">
            <div className={`status-dot ${isConnected ? 'connected' : ''}`} />
            <span>
              {isConnected ? 'Connected' : 'Disconnected'} ({connectionState})
            </span>
          </div>
          {isStreaming && (
            <div style={{ color: '#28a745', fontWeight: 600 }}>
              🎤 Audio Active
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error.message}
          </div>
        )}

        {/* Controls */}
        <div className="controls">
          <button
            className="btn-primary"
            onClick={handleConnect}
            disabled={isConnected}
          >
            Connect
          </button>
          <button
            className="btn-danger"
            onClick={handleDisconnect}
            disabled={!isConnected}
          >
            Disconnect
          </button>
          <button
            className="btn-success"
            onClick={handleStartAudio}
            disabled={!isConnected || isStreaming}
          >
            Start Audio
          </button>
          <button
            className="btn-danger"
            onClick={stopStream}
            disabled={!isStreaming}
          >
            Stop Audio
          </button>
        </div>

        {/* Audio Visualizer */}
        <div className="audio-visualizer">
          {isStreaming ? '🎤 Audio streaming...' : 'Audio inactive'}
        </div>

        {/* Gemini Configuration Panel */}
        <GeminiConfigPanel onApply={handleApplyGeminiConfig} />

        {/* Chat Interface */}
        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#6c757d' }}>
                No messages yet. Start chatting with Gemini!
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`message ${msg.type === 'text' ? 'sent' : 'received'}`}
                >
                  <div>{msg.content}</div>
                  <div className="message-time">
                    {new Date(msg.timestamp || 0).toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="input-group">
            <input
              type="text"
              placeholder="Type a message..."
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={!isConnected}
            />
            <button
              className="btn-primary"
              onClick={handleSendMessage}
              disabled={!isConnected || !messageInput.trim()}
            >
              Send
            </button>
            <button
              className="btn-danger"
              onClick={clearMessages}
              disabled={messages.length === 0}
            >
              Clear
            </button>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="stats">
            <div className="stat-card">
              <div className="stat-label">Bytes Sent</div>
              <div className="stat-value">
                {(stats.bytesSent / 1024).toFixed(2)} KB
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Bytes Received</div>
              <div className="stat-value">
                {(stats.bytesReceived / 1024).toFixed(2)} KB
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Packets Lost</div>
              <div className="stat-value">{stats.packetsLost}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Round Trip Time</div>
              <div className="stat-value">
                {(stats.currentRoundTripTime * 1000).toFixed(0)} ms
              </div>
            </div>
          </div>
        )}

        {/* Hidden audio elements */}
        <audio ref={localAudioRef} autoPlay muted style={{ display: 'none' }} />
        <audio ref={remoteAudioRef} autoPlay style={{ display: 'none' }} />
      </div>
    </div>
  );
}

export default App;
