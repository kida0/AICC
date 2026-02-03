/**
 * Call history page
 */
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCall } from '../hooks/useCall';
import { CallList } from '../components/CallHistory';
import { Button, Loading } from '../components/common';
import './HistoryPage.css';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const { callHistory, loading, loadCallHistory } = useCall();

  useEffect(() => {
    loadCallHistory();
  }, [loadCallHistory]);

  return (
    <div className="history-page">
      <div className="history-container">
        <div className="history-header">
          <h1>통화 내역</h1>
          <Button onClick={() => navigate('/')} variant="primary">
            새 통화 시작
          </Button>
        </div>

        {loading ? (
          <Loading text="통화 내역을 불러오는 중..." />
        ) : (
          <CallList calls={callHistory} />
        )}
      </div>
    </div>
  );
};
