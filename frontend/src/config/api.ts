/**
 * API configuration
 */

export const API_BASE_URL = import.meta.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
export const WS_BASE_URL = import.meta.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8000';

export const API_ENDPOINTS = {
  // Calls
  CALLS: '/api/v1/calls',
  INITIATE_CALL: '/api/v1/calls/initiate',
  GET_CALL: (callId: string) => `/api/v1/calls/${callId}`,
  END_CALL: (callId: string) => `/api/v1/calls/${callId}`,

  // Transcripts
  GET_TRANSCRIPTS: (callId: string) => `/api/v1/transcripts/${callId}`,

  // Recordings
  GET_RECORDING: (callId: string) => `/api/v1/recordings/${callId}`,

  // WebSocket
  WS_CALL: (callId: string) => `/ws/call/${callId}`,
};
