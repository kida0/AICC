/**
 * Transcript-related type definitions
 */

export type SpeakerType = 'user' | 'ai';

export interface Transcript {
  id: string;
  call_id: string;
  speaker: SpeakerType;
  text: string;
  timestamp: string;
  confidence?: number;
  created_at: string;
}

export interface TranscriptListResponse {
  call_id: string;
  transcripts: Transcript[];
}

export interface WebSocketTranscriptMessage {
  type: 'transcript';
  speaker: SpeakerType;
  text: string;
  timestamp: string;
}
