/**
 * Call state slice
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { callService } from '../../services/api/callService';
import type { Call, CallInitiateRequest, CallListResponse } from '../../types/call';
import type { Transcript } from '../../types/transcript';

interface CallState {
  activeCall: Call | null;
  callHistory: Call[];
  transcripts: Transcript[];
  loading: boolean;
  error: string | null;
  totalCalls: number;
  currentPage: number;
}

const initialState: CallState = {
  activeCall: null,
  callHistory: [],
  transcripts: [],
  loading: false,
  error: null,
  totalCalls: 0,
  currentPage: 1,
};

// Async thunks
export const initiateCall = createAsyncThunk(
  'call/initiate',
  async (data: CallInitiateRequest) => {
    const response = await callService.initiateCall(data);
    // Fetch full call details
    const call = await callService.getCall(response.call_id);
    return { call, websocketUrl: response.websocket_url };
  }
);

export const fetchCallHistory = createAsyncThunk(
  'call/fetchHistory',
  async (params?: { page?: number; page_size?: number }) => {
    const response = await callService.getCalls(params);
    return response;
  }
);

export const fetchCallDetails = createAsyncThunk(
  'call/fetchDetails',
  async (callId: string) => {
    const call = await callService.getCall(callId);
    const transcripts = await callService.getTranscripts(callId);
    return { call, transcripts: transcripts.transcripts };
  }
);

export const endCall = createAsyncThunk(
  'call/end',
  async (callId: string) => {
    await callService.endCall(callId);
    return callId;
  }
);

// Slice
const callSlice = createSlice({
  name: 'call',
  initialState,
  reducers: {
    setActiveCall: (state, action: PayloadAction<Call>) => {
      state.activeCall = action.payload;
    },
    updateCallStatus: (state, action: PayloadAction<{ callId: string; status: string }>) => {
      if (state.activeCall?.id === action.payload.callId) {
        state.activeCall.status = action.payload.status as any;
      }
    },
    addTranscript: (state, action: PayloadAction<Transcript>) => {
      state.transcripts.push(action.payload);
    },
    clearActiveCall: (state) => {
      state.activeCall = null;
      state.transcripts = [];
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Initiate call
    builder.addCase(initiateCall.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(initiateCall.fulfilled, (state, action) => {
      state.loading = false;
      state.activeCall = action.payload.call;
      state.transcripts = [];
    });
    builder.addCase(initiateCall.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to initiate call';
    });

    // Fetch call history
    builder.addCase(fetchCallHistory.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(fetchCallHistory.fulfilled, (state, action) => {
      state.loading = false;
      state.callHistory = action.payload.items;
      state.totalCalls = action.payload.total;
      state.currentPage = action.payload.page;
    });
    builder.addCase(fetchCallHistory.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch call history';
    });

    // Fetch call details
    builder.addCase(fetchCallDetails.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(fetchCallDetails.fulfilled, (state, action) => {
      state.loading = false;
      state.activeCall = action.payload.call;
      state.transcripts = action.payload.transcripts;
    });
    builder.addCase(fetchCallDetails.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch call details';
    });

    // End call
    builder.addCase(endCall.fulfilled, (state) => {
      if (state.activeCall) {
        state.activeCall.status = 'completed';
      }
    });
  },
});

export const {
  setActiveCall,
  updateCallStatus,
  addTranscript,
  clearActiveCall,
  setError,
  clearError,
} = callSlice.actions;

export default callSlice.reducer;
