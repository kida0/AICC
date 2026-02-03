/**
 * Call-related type definitions
 */

export type CallStatus =
  | 'initiating'
  | 'ringing'
  | 'in_progress'
  | 'completed'
  | 'failed';

export interface Call {
  id: string;
  phone_number: string;
  status: CallStatus;
  caller_id?: string;
  direction: string;
  twilio_call_sid?: string;
  started_at?: string;
  ended_at?: string;
  duration?: number;
  recording_url?: string;
  ai_persona: string;
  created_at: string;
  updated_at: string;
}

export interface CallInitiateRequest {
  phone_number: string;
  caller_id?: string;
  ai_persona?: string;
}

export interface CallInitiateResponse {
  call_id: string;
  status: string;
  phone_number: string;
  created_at: string;
  websocket_url: string;
}

export interface CallListResponse {
  items: Call[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
