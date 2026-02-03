/**
 * Call status indicator component
 */
import React from 'react';
import type { CallStatus } from '../../types/call';
import './StatusIndicator.css';

interface StatusIndicatorProps {
  status: CallStatus;
}

const statusLabels: Record<CallStatus, string> = {
  initiating: '전화 거는 중',
  ringing: '연결 중',
  in_progress: '통화 중',
  completed: '통화 종료',
  failed: '통화 실패',
};

const statusColors: Record<CallStatus, string> = {
  initiating: '#f59e0b',
  ringing: '#3b82f6',
  in_progress: '#10b981',
  completed: '#6b7280',
  failed: '#ef4444',
};

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status }) => {
  return (
    <div className="status-indicator">
      <div
        className="status-dot"
        style={{ backgroundColor: statusColors[status] }}
      />
      <span className="status-label">{statusLabels[status]}</span>
    </div>
  );
};
