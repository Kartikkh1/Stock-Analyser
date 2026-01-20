import React from 'react';
import './ProgressBar.css';

const ProgressBar = ({ progress, statusMessage, isVisible }) => {
  if (!isVisible) {
    return null;
  }

  return (
    <div className="progress-card card">
      <h3>Analysis in Progress</h3>
      <div className="progress-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="progress-text">{progress}%</div>
      </div>
      {statusMessage && (
        <p className="progress-status-message">
          <span className="progress-spinner"></span>
          {statusMessage}
        </p>
      )}
    </div>
  );
};

export default ProgressBar;
