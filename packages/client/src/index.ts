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
} from './types';
export type {
  UseWebRTCOptions,
  UseWebRTCReturn,
  UseMediaStreamReturn,
  UseDataChannelReturn,
  UseRemoteTracksReturn,
} from './hooks';
