/**
 * Home page - Call initiation
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { PhoneInput } from '../components/CallInitiation';
import { useCall } from '../hooks/useCall';
import './HomePage.css';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { startCall, loading, error } = useCall();

  const handleInitiateCall = async (phoneNumber: string) => {
    try {
      const result = await startCall({ phone_number: phoneNumber });
      if (result && result.call) {
        // Navigate to call page
        navigate(`/call/${result.call.id}`);
      }
    } catch (err) {
      console.error('Failed to initiate call:', err);
    }
  };

  return (
    <div className="home-page">
      <div className="home-header">
        <h1>AICC</h1>
        <p>AI Call Center</p>
      </div>

      {error && (
        <div className="home-error">
          <p>오류: {error}</p>
        </div>
      )}

      <PhoneInput onSubmit={handleInitiateCall} loading={loading} />

      <div className="home-footer">
        <button onClick={() => navigate('/history')} className="home-link">
          통화 내역 보기 →
        </button>
      </div>
    </div>
  );
};
