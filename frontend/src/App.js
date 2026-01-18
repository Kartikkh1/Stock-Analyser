import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [stockTicker, setStockTicker] = useState('');
  const [llmChoice, setLlmChoice] = useState('openai');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [report, setReport] = useState('');
  const [error, setError] = useState('');
  const wsRef = useRef(null);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    if (!stockTicker.trim()) {
      setError('Please enter a stock ticker');
      return;
    }

    // Reset states
    setError('');
    setReport('');
    setProgress(0);
    setStatusMessage('Connecting to server...');
    setIsAnalyzing(true);

    // Create WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws/report');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      // Send initial request
      ws.send(JSON.stringify({
        stock_ticker: stockTicker.toUpperCase().trim(),
        llm_choice: llmChoice
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);

      if (data.error) {
        setError(data.error);
        setIsAnalyzing(false);
        ws.close();
        return;
      }

      if (data.status) {
        setStatusMessage(data.message || '');
        setProgress(data.progress || 0);

        if (data.status === 'completed') {
          setReport(data.report || '');
          setIsAnalyzing(false);
          ws.close();
        } else if (data.status === 'error') {
          setError(data.message || 'An error occurred during analysis');
          setIsAnalyzing(false);
          ws.close();
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please ensure the backend server is running.');
      setIsAnalyzing(false);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      if (isAnalyzing && !report) {
        setError('Connection closed unexpectedly');
        setIsAnalyzing(false);
      }
    };
  };

  const handleCancel = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setIsAnalyzing(false);
    setStatusMessage('Analysis cancelled');
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1 className="title">📈 Stock Analyzer</h1>
          <p className="subtitle">AI-Powered Stock Analysis & Reporting</p>
        </header>

        <div className="content">
          {/* Form Section */}
          <div className="card form-card">
            <h2>Generate Analysis Report</h2>
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label htmlFor="stockTicker" className="label">
                  Stock Ticker Symbol
                </label>
                <input
                  type="text"
                  id="stockTicker"
                  className="input"
                  value={stockTicker}
                  onChange={(e) => setStockTicker(e.target.value)}
                  placeholder="e.g., AAPL, TSLA, MSFT"
                  disabled={isAnalyzing}
                  required
                />
                <small className="hint">Enter the stock ticker symbol you want to analyze</small>
              </div>

              <div className="form-group">
                <label className="label">Select LLM Provider</label>
                <div className="radio-group">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="llmChoice"
                      value="openai"
                      checked={llmChoice === 'openai'}
                      onChange={(e) => setLlmChoice(e.target.value)}
                      disabled={isAnalyzing}
                    />
                    <span className="radio-text">
                      <strong>OpenAI</strong>
                      <small>GPT-4 powered analysis</small>
                    </span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="llmChoice"
                      value="anthropic"
                      checked={llmChoice === 'anthropic'}
                      onChange={(e) => setLlmChoice(e.target.value)}
                      disabled={isAnalyzing}
                    />
                    <span className="radio-text">
                      <strong>Anthropic</strong>
                      <small>Claude powered analysis</small>
                    </span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="llmChoice"
                      value="gemini"
                      checked={llmChoice === 'gemini'}
                      onChange={(e) => setLlmChoice(e.target.value)}
                      disabled={isAnalyzing}
                    />
                    <span className="radio-text">
                      <strong>Google Gemini</strong>
                      <small>Gemini powered analysis</small>
                    </span>
                  </label>
                </div>
              </div>

              {error && (
                <div className="alert alert-error">
                  <span className="alert-icon">⚠️</span>
                  {error}
                </div>
              )}

              <div className="button-group">
                {!isAnalyzing ? (
                  <button type="submit" className="button button-primary">
                    Generate Report
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleCancel}
                    className="button button-secondary"
                  >
                    Cancel Analysis
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Progress Section */}
          {isAnalyzing && (
            <div className="card progress-card">
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
                <p className="status-message">
                  <span className="spinner"></span>
                  {statusMessage}
                </p>
              )}
            </div>
          )}

          {/* Report Section */}
          {report && (
            <div className="card report-card">
              <div className="report-header">
                <h2>Analysis Report</h2>
                <button
                  className="button button-small"
                  onClick={() => {
                    const blob = new Blob([report], { type: 'text/markdown' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${stockTicker}_${llmChoice}_report.md`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                >
                  Download Report
                </button>
              </div>
              <div className="report-content">
                <pre>{report}</pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
