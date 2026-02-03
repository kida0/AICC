/**
 * Call detail page - View past call with audio and transcripts
 */
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCall } from '../hooks/useCall';
import { StatusIndicator, TranscriptDisplay } from '../components/CallStatus';
import { AudioPlayer } from '../components/CallDetails';
import { Button, Loading } from '../components/common';
import { callService } from '../services/api/callService';
import './CallDetailPage.css';

export const CallDetailPage: React.FC = () => {
  const { callId } = useParams<{ callId: string }>();
  const navigate = useNavigate();
  const { activeCall, transcripts, loading, loadCallDetails } = useCall();

  useEffect(() => {
    if (callId) {
      loadCallDetails(callId);
    }
  }, [callId, loadCallDetails]);

  if (loading || !activeCall) {
    return (
      <div className="call-detail-page">
        <Loading text="통화 정보를 불러오는 중..." />
      </div>
    );
  }

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}분 ${secs}초`;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR');
  };

  return (
    <div className="call-detail-page">
      <div className="call-detail-container">
        <Button onClick={() => navigate('/history')} variant="secondary">
          ← 목록으로
        </Button>

        <h1 className="call-detail-title">통화 상세</h1>

        <div className="call-detail-info">
          <div className="call-detail-row">
            <span className="call-detail-label">전화번호</span>
            <span className="call-detail-value">{activeCall.phone_number}</span>
          </div>
          <div className="call-detail-row">
            <span className="call-detail-label">상태</span>
            <StatusIndicator status={activeCall.status} />
          </div>
          <div className="call-detail-row">
            <span className="call-detail-label">시작 시간</span>
            <span className="call-detail-value">
              {formatDate(activeCall.created_at)}
            </span>
          </div>
          {activeCall.duration && (
            <div className="call-detail-row">
              <span className="call-detail-label">통화 시간</span>
              <span className="call-detail-value">
                {formatDuration(activeCall.duration)}
              </span>
            </div>
          )}
        </div>

        {activeCall.recording_url && (
          <div className="call-detail-section">
            <h2>녹음 파일</h2>
            <AudioPlayer
              audioUrl={callService.getRecordingUrl(activeCall.id)}
            />
          </div>
        )}

        <div className="call-detail-section">
          <h2>대화 내용</h2>
          <TranscriptDisplay transcripts={transcripts} />
        </div>
      </div>
    </div>
  );
};
