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
  type: 'text' | 'binary' | 'json' | 'config';
  content: any;
  timestamp?: number;
  gemini_config?: GeminiConfig;
}

export interface SignalingMessage {
  type: 'offer' | 'answer' | 'ice-candidate' | 'error' | 'ready' | 'config';
  data?: any;
  sessionId?: string;
  gemini_config?: GeminiConfig;
}

// Gemini Configuration Types
export interface GeminiGenerationConfig {
  temperature?: number;
  top_p?: number;
  top_k?: number;
  max_output_tokens?: number;
  candidate_count?: number;
  stop_sequences?: string[];
  presence_penalty?: number;
  frequency_penalty?: number;
}

export interface GeminiVoiceConfig {
  voice_name?: string; // Options: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr
  preemptive_interruption?: boolean;
}

export interface GeminiVADConfig {
  start_of_speech_sensitivity?: number; // 0.0 to 1.0
  end_of_speech_sensitivity?: number; // 0.0 to 1.0
  prefix_padding_ms?: number;
  silence_duration_ms?: number;
}

export interface GeminiSpeechConfig {
  language_code?: string; // BCP-47 format, e.g., "en-US", "de-DE", "ja-JP"
  vad_config?: GeminiVADConfig;
}

export interface GeminiTranscriptionConfig {
  enable_input_transcription?: boolean;
  enable_output_transcription?: boolean;
}

export interface GeminiNativeAudioConfig {
  enable_affective_dialog?: boolean; // Emotion-aware dialogue
  enable_proactive_audio?: boolean; // Proactive responses
  thinking_budget?: number; // Thinking time in seconds, 0 to disable
}

export interface GeminiSessionConfig {
  enable_context_window_compression?: boolean;
  compression_token_threshold?: number;
  enable_session_resumption?: boolean;
  session_resumption_handle?: string;
}

export interface GeminiToolConfig {
  // Function calling
  function_declarations?: any[];
  enable_automatic_function_calling?: boolean;
  function_behavior?: 'BLOCKING' | 'NON_BLOCKING';
  response_scheduling?: 'INTERRUPT' | 'WHEN_IDLE' | 'SILENT';

  // Built-in tools
  enable_code_execution?: boolean;
  enable_google_search?: boolean;
  enable_url_context?: boolean;
}

export interface GeminiConfig {
  // Model configuration
  model_name?: string;
  system_instruction?: string;

  // Response configuration
  response_modalities?: string[];
  media_resolution?: 'low' | 'medium' | 'high';

  // Generation settings
  generation_config?: GeminiGenerationConfig;

  // Voice and speech settings
  voice_config?: GeminiVoiceConfig;
  speech_config?: GeminiSpeechConfig;

  // Transcription settings
  transcription_config?: GeminiTranscriptionConfig;

  // Native audio features
  native_audio_config?: GeminiNativeAudioConfig;

  // Session management
  session_config?: GeminiSessionConfig;

  // Tools and function calling
  tool_config?: GeminiToolConfig;
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
