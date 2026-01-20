import React from 'react';
import './ReportDisplay.css';

const ReportDisplay = ({ report, stockTicker, llmChoice }) => {
  if (!report) {
    return null;
  }

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${stockTicker}_${llmChoice}_report.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="report-card card">
      <div className="report-header">
        <h2>Analysis Report</h2>
        <button
          className="report-download-button button button-small"
          onClick={handleDownload}
        >
          Download Report
        </button>
      </div>
      <div className="report-content">
        <pre>{report}</pre>
      </div>
    </div>
  );
};

export default ReportDisplay;
