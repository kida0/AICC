/**
 * Call history list component
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Call } from '../../types/call';
import { StatusIndicator } from '../CallStatus';
import './CallList.css';

interface CallListProps {
  calls: Call[];
  loading?: boolean;
}

export const CallList: React.FC<CallListProps> = ({ calls, loading = false }) => {
  const navigate = useNavigate();

  if (loading) {
    return <div className="call-list-loading">로딩 중...</div>;
  }

  if (calls.length === 0) {
    return (
      <div className="call-list-empty">
        <p>통화 내역이 없습니다.</p>
      </div>
    );
  }

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR');
  };

  return (
    <div className="call-list">
      {calls.map((call) => (
        <div
          key={call.id}
          className="call-list-item"
          onClick={() => navigate(`/call/${call.id}`)}
        >
          <div className="call-list-item-header">
            <span className="call-list-phone">{call.phone_number}</span>
            <StatusIndicator status={call.status} />
          </div>

          <div className="call-list-item-details">
            <span>시작: {formatDate(call.created_at)}</span>
            {call.duration && (
              <span>통화 시간: {formatDuration(call.duration)}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
