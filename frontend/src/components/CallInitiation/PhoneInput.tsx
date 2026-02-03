/**
 * Phone number input component with validation
 */
import React, { useState } from 'react';
import { Input, Button } from '../common';
import './PhoneInput.css';

interface PhoneInputProps {
  onSubmit: (phoneNumber: string) => void;
  loading?: boolean;
}

export const PhoneInput: React.FC<PhoneInputProps> = ({ onSubmit, loading = false }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState('');

  const validatePhoneNumber = (number: string): boolean => {
    // E.164 format validation (starting with +)
    const e164Regex = /^\+[1-9]\d{1,14}$/;
    return e164Regex.test(number);
  };

  const handleSubmit = () => {
    setError('');

    if (!phoneNumber.trim()) {
      setError('전화번호를 입력해주세요');
      return;
    }

    if (!validatePhoneNumber(phoneNumber)) {
      setError('E.164 형식으로 입력해주세요 (예: +821012345678)');
      return;
    }

    onSubmit(phoneNumber);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleSubmit();
    }
  };

  return (
    <div className="phone-input-container">
      <h2>AI 상담사 통화</h2>
      <p className="phone-input-description">
        전화번호를 입력하면 자동으로 전화를 걸어 AI 상담사와 통화할 수 있습니다.
      </p>

      <div className="phone-input-form">
        <Input
          type="tel"
          value={phoneNumber}
          onChange={setPhoneNumber}
          placeholder="+821012345678"
          label="전화번호 (E.164 형식)"
          error={error}
          disabled={loading}
          fullWidth
        />

        <Button
          onClick={handleSubmit}
          disabled={loading || !phoneNumber.trim()}
          variant="primary"
          fullWidth
        >
          {loading ? '전화 거는 중...' : '전화 걸기'}
        </Button>
      </div>

      <div className="phone-input-help">
        <p><strong>E.164 형식 예시:</strong></p>
        <ul>
          <li>한국: +821012345678</li>
          <li>미국: +11234567890</li>
        </ul>
      </div>
    </div>
  );
};
