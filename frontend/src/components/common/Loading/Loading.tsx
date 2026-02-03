/**
 * Loading spinner component
 */
import React from 'react';
import './Loading.css';

interface LoadingProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
}

export const Loading: React.FC<LoadingProps> = ({ size = 'medium', text }) => {
  return (
    <div className="loading-container">
      <div className={`loading-spinner loading-${size}`}></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
};
