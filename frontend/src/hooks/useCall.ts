/**
 * Custom hook for call management
 */
import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import {
  initiateCall,
  endCall,
  fetchCallHistory,
  fetchCallDetails,
  addTranscript,
  updateCallStatus,
  clearActiveCall,
} from '../store/slices/callSlice';
import type { CallInitiateRequest } from '../types/call';
import type { Transcript } from '../types/transcript';

export const useCall = () => {
  const dispatch = useAppDispatch();
  const {
    activeCall,
    callHistory,
    transcripts,
    loading,
    error,
    totalCalls,
    currentPage,
  } = useAppSelector((state) => state.call);

  const startCall = useCallback(
    async (data: CallInitiateRequest) => {
      const result = await dispatch(initiateCall(data));
      return result.payload;
    },
    [dispatch]
  );

  const stopCall = useCallback(
    async (callId: string) => {
      await dispatch(endCall(callId));
    },
    [dispatch]
  );

  const loadCallHistory = useCallback(
    async (page: number = 1, pageSize: number = 20) => {
      await dispatch(fetchCallHistory({ page, page_size: pageSize }));
    },
    [dispatch]
  );

  const loadCallDetails = useCallback(
    async (callId: string) => {
      await dispatch(fetchCallDetails(callId));
    },
    [dispatch]
  );

  const handleNewTranscript = useCallback(
    (transcript: Transcript) => {
      dispatch(addTranscript(transcript));
    },
    [dispatch]
  );

  const handleStatusUpdate = useCallback(
    (callId: string, status: string) => {
      dispatch(updateCallStatus({ callId, status }));
    },
    [dispatch]
  );

  const clearCall = useCallback(() => {
    dispatch(clearActiveCall());
  }, [dispatch]);

  return {
    // State
    activeCall,
    callHistory,
    transcripts,
    loading,
    error,
    totalCalls,
    currentPage,

    // Actions
    startCall,
    stopCall,
    loadCallHistory,
    loadCallDetails,
    handleNewTranscript,
    handleStatusUpdate,
    clearCall,
  };
};
