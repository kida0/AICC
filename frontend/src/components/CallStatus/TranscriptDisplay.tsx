/**
 * Real-time transcript display component
 */
import React, { useEffect, useRef } from 'react';
import type { Transcript } from '../../types/transcript';
import './TranscriptDisplay.css';

interface TranscriptDisplayProps {
  transcripts: Transcript[];
}

export const TranscriptDisplay: React.FC<TranscriptDisplayProps> = ({ transcripts }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new transcript is added
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [transcripts]);

  if (transcripts.length === 0) {
    return (
      <div className="transcript-display">
        <p className="transcript-empty">대화가 시작되면 여기에 내용이 표시됩니다.</p>
      </div>
    );
  }

  return (
    <div className="transcript-display" ref={containerRef}>
      {transcripts.map((transcript, index) => (
        <div
          key={index}
          className={`transcript-item transcript-${transcript.speaker}`}
        >
          <div className="transcript-speaker">
            {transcript.speaker === 'user' ? '사용자' : 'AI 상담사'}
          </div>
          <div className="transcript-text">{transcript.text}</div>
          <div className="transcript-time">
            {new Date(transcript.timestamp).toLocaleTimeString('ko-KR')}
          </div>
        </div>
      ))}
    </div>
  );
};
