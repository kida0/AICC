/**
 * Call API service
 */
import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../../config/api';
import type {
  CallInitiateRequest,
  CallInitiateResponse,
  Call,
  CallListResponse
} from '../../types/call';
import type { TranscriptListResponse } from '../../types/transcript';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const callService = {
  /**
   * Initiate a new call
   */
  initiateCall: async (data: CallInitiateRequest): Promise<CallInitiateResponse> => {
    const response = await apiClient.post<CallInitiateResponse>(
      API_ENDPOINTS.INITIATE_CALL,
      data
    );
    return response.data;
  },

  /**
   * Get call details
   */
  getCall: async (callId: string): Promise<Call> => {
    const response = await apiClient.get<Call>(
      API_ENDPOINTS.GET_CALL(callId)
    );
    return response.data;
  },

  /**
   * Get list of calls
   */
  getCalls: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<CallListResponse> => {
    const response = await apiClient.get<CallListResponse>(
      API_ENDPOINTS.CALLS,
      { params }
    );
    return response.data;
  },

  /**
   * End an active call
   */
  endCall: async (callId: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.END_CALL(callId));
  },

  /**
   * Get call transcripts
   */
  getTranscripts: async (callId: string): Promise<TranscriptListResponse> => {
    const response = await apiClient.get<TranscriptListResponse>(
      API_ENDPOINTS.GET_TRANSCRIPTS(callId)
    );
    return response.data;
  },

  /**
   * Get recording URL
   */
  getRecordingUrl: (callId: string): string => {
    return `${API_BASE_URL}${API_ENDPOINTS.GET_RECORDING(callId)}`;
  },
};
