/**
 * @webrtc-enterprise/client
 * Enterprise-grade WebRTC client library
 */

export { WebRTCClient } from './WebRTCClient';
export {
  useWebRTC,
  useMediaStream,
  useDataChannel,
  useRemoteTracks,
} from './hooks';
export type {
  RTCConfig,
  MediaConfig,
  DataMessage,
  SignalingMessage,
  ConnectionStats,
  WebRTCClientEvents,
  WebRTCClientInterface,
  GeminiConfig,
  GeminiGenerationConfig,
  GeminiVoiceConfig,
  GeminiVADConfig,
  GeminiSpeechConfig,
  GeminiTranscriptionConfig,
  GeminiNativeAudioConfig,
  GeminiSessionConfig,
  GeminiToolConfig,
} from './types';
export type {
  UseWebRTCOptions,
  UseWebRTCReturn,
  UseMediaStreamReturn,
  UseDataChannelReturn,
  UseRemoteTracksReturn,
} from './hooks';
