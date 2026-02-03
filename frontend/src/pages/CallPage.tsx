/**
 * Active call page - Real-time status and transcripts
 */
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCall } from '../hooks/useCall';
import { useWebSocket } from '../hooks/useWebSocket';
import { StatusIndicator, TranscriptDisplay } from '../components/CallStatus';
import { Button, Loading } from '../components/common';
import type { WebSocketTranscriptMessage } from '../types/transcript';
import './CallPage.css';

export const CallPage: React.FC = () => {
  const { callId } = useParams<{ callId: string }>();
  const navigate = useNavigate();
  const {
    activeCall,
    transcripts,
    loading,
    loadCallDetails,
    stopCall,
    handleNewTranscript,
    handleStatusUpdate,
  } = useCall();

  // Load call details on mount
  useEffect(() => {
    if (callId) {
      loadCallDetails(callId);
    }
  }, [callId, loadCallDetails]);

  // WebSocket connection for real-time updates
  useWebSocket(callId || null, {
    onMessage: (message) => {
      console.log('WebSocket message received:', message);

      if (message.type === 'transcript') {
        const transcriptMsg = message as WebSocketTranscriptMessage;
        handleNewTranscript({
          id: crypto.randomUUID(),
          call_id: callId!,
          speaker: transcriptMsg.speaker,
          text: transcriptMsg.text,
          timestamp: transcriptMsg.timestamp,
          created_at: transcriptMsg.timestamp,
        });
      } else if (message.type === 'status_update') {
        handleStatusUpdate(callId!, message.status);
      }
    },
  });

  const handleEndCall = async () => {
    if (callId) {
      await stopCall(callId);
      setTimeout(() => {
        navigate('/history');
      }, 1000);
    }
  };

  if (loading || !activeCall) {
    return (
      <div className="call-page">
        <Loading text="통화 정보를 불러오는 중..." />
      </div>
    );
  }

  return (
    <div className="call-page">
      <div className="call-container">
        <h1 className="call-title">통화 중</h1>

        <div className="call-info">
          <div className="call-phone-number">{activeCall.phone_number}</div>
          <StatusIndicator status={activeCall.status} />
        </div>

        <div className="call-transcripts-section">
          <h2>대화 내용</h2>
          <TranscriptDisplay transcripts={transcripts} />
        </div>

        <div className="call-actions">
          <Button
            onClick={handleEndCall}
            variant="danger"
            disabled={activeCall.status === 'completed'}
            fullWidth
          >
            {activeCall.status === 'completed' ? '통화 종료됨' : '통화 종료'}
          </Button>

          <Button
            onClick={() => navigate('/history')}
            variant="secondary"
            fullWidth
          >
            통화 내역으로 이동
          </Button>
        </div>
      </div>
    </div>
  );
};
