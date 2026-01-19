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
  const [tickerError, setTickerError] = useState('');
  const [isTickerValid, setIsTickerValid] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [companyInfo, setCompanyInfo] = useState(null);
  const [isCancelling, setIsCancelling] = useState(false);
  const wsRef = useRef(null);
  const validationTimeoutRef = useRef(null);

  // Cleanup WebSocket and timeout on unmount
  useEffect(() => {
    return () => {
      // Clear any pending cancel timeout
      if (wsRef.current && wsRef.current.cancelTimeout) {
        clearTimeout(wsRef.current.cancelTimeout);
      }
      
      // Send cancel message if WebSocket is still open
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(JSON.stringify({ action: 'cancel' }));
        } catch (error) {
          console.error('Error sending cancel on unmount:', error);
        }
        wsRef.current.close();
      }
      
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }
    };
  }, []);

  // Validate ticker format (client-side)
  const validateTickerFormat = (ticker) => {
    const trimmedTicker = ticker.trim().toUpperCase();
    
    // Empty ticker
    if (!trimmedTicker) {
      return { valid: false, error: '' };
    }
    
    // Check if it contains only letters
    if (!/^[A-Z]+$/.test(trimmedTicker)) {
      return { valid: false, error: 'Ticker should contain only letters' };
    }
    
    // Check length (most stock tickers are 1-5 characters)
    if (trimmedTicker.length < 1 || trimmedTicker.length > 5) {
      return { valid: false, error: 'Ticker should be 1-5 characters long' };
    }
    
    return { valid: true, error: '' };
  };

  // Validate ticker with backend API
  const validateTickerWithAPI = async (ticker) => {
    const trimmedTicker = ticker.trim().toUpperCase();
    
    if (!trimmedTicker) {
      return;
    }
    
    setIsValidating(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/validate-ticker', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticker: trimmedTicker }),
      });
      
      const data = await response.json();
      
      if (data.valid) {
        setIsTickerValid(true);
        setTickerError('');
        setCompanyInfo(data);
      } else {
        setIsTickerValid(false);
        setTickerError(data.message || 'Ticker symbol not found');
        setCompanyInfo(null);
      }
    } catch (err) {
      console.error('Ticker validation error:', err);
      // On network error, fall back to format-only validation
      setTickerError('Unable to verify ticker. Please check your connection.');
      setIsTickerValid(false);
      setCompanyInfo(null);
    } finally {
      setIsValidating(false);
    }
  };

  // Handle ticker input change with debounced API validation
  const handleTickerChange = (e) => {
    const value = e.target.value.toUpperCase();
    setStockTicker(value);
    
    // Clear previous timeout
    if (validationTimeoutRef.current) {
      clearTimeout(validationTimeoutRef.current);
    }
    
    // Reset states
    setCompanyInfo(null);
    
    // First, validate format
    const formatValidation = validateTickerFormat(value);
    
    if (!formatValidation.valid) {
      setTickerError(formatValidation.error);
      setIsTickerValid(false);
      return;
    }
    
    // If format is valid, validate with API after debounce
    setTickerError('');
    validationTimeoutRef.current = setTimeout(() => {
      validateTickerWithAPI(value);
    }, 500); // 500ms debounce
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    if (!stockTicker.trim()) {
      setError('Please enter a stock ticker');
      return;
    }

    if (!isTickerValid) {
      setError('Please enter a valid stock ticker symbol');
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
        } else if (data.status === 'cancelled') {
          console.log('Received cancellation confirmation from server');
          setStatusMessage('Analysis cancelled successfully');
          setIsAnalyzing(false);
          setIsCancelling(false);
          setProgress(0);
          
          // Clear the safety timeout since we got proper confirmation
          if (ws.cancelTimeout) {
            clearTimeout(ws.cancelTimeout);
          }
          
          // Now close the WebSocket after receiving confirmation
          ws.close();
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please ensure the backend server is running.');
      setIsAnalyzing(false);
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed', event);
      
      // Clear any pending cancel timeout
      if (ws.cancelTimeout) {
        clearTimeout(ws.cancelTimeout);
      }
    };
  };

  const handleCancel = () => {
    setIsCancelling(true);
    setStatusMessage('Cancelling analysis...');
    
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Send cancel message to server
      try {
        wsRef.current.send(JSON.stringify({ action: 'cancel' }));
        console.log('Cancel message sent to server, waiting for confirmation...');
        
        // The WebSocket will be closed when we receive the "cancelled" status from server
        // or after a safety timeout to prevent hanging
        const safetyTimeout = setTimeout(() => {
          console.log('Safety timeout: forcing WebSocket close');
          if (wsRef.current) {
            wsRef.current.close();
          }
          setIsCancelling(false);
          setIsAnalyzing(false);
          setProgress(0);
        }, 3000); // 3 second safety timeout
        
        // Store timeout so we can clear it when server responds
        wsRef.current.cancelTimeout = safetyTimeout;
      } catch (error) {
        console.error('Error sending cancel message:', error);
        // Close anyway if sending fails
        if (wsRef.current) {
          wsRef.current.close();
        }
        setIsCancelling(false);
        setIsAnalyzing(false);
        setProgress(0);
      }
    } else {
      setIsCancelling(false);
      setIsAnalyzing(false);
      setProgress(0);
    }
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
                <div className="input-wrapper">
                  <input
                    type="text"
                    id="stockTicker"
                    className={`input ${stockTicker && (isTickerValid ? 'input-valid' : tickerError ? 'input-invalid' : '')}`}
                    value={stockTicker}
                    onChange={handleTickerChange}
                    placeholder="e.g., AAPL, TSLA, MSFT"
                    disabled={isAnalyzing}
                    maxLength={5}
                    required
                  />
                  {stockTicker && !isValidating && (
                    <span className={`validation-icon ${isTickerValid ? 'valid' : 'invalid'}`}>
                      {isTickerValid ? '✓' : '✗'}
                    </span>
                  )}
                  {isValidating && (
                    <span className="validation-spinner"></span>
                  )}
                </div>
                {tickerError && stockTicker && !isValidating && (
                  <small className="error-hint">{tickerError}</small>
                )}
                {!tickerError && !stockTicker && (
                  <small className="hint">Enter a 1-5 letter stock ticker symbol (e.g., AAPL, TSLA)</small>
                )}
                {isValidating && (
                  <small className="hint">Validating ticker symbol...</small>
                )}
                {isTickerValid && companyInfo && !isValidating && (
                  <div className="company-info">
                    <small className="success-hint">
                      ✓ Valid: <strong>{companyInfo.company_name}</strong>
                    </small>
                    {companyInfo.exchange && companyInfo.country && (
                      <small className="info-hint">
                        {companyInfo.exchange} • {companyInfo.country}
                        {companyInfo.industry && ` • ${companyInfo.industry}`}
                      </small>
                    )}
                  </div>
                )}
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
                    disabled={isCancelling}
                  >
                    {isCancelling ? (
                      <>
                        <span className="button-spinner"></span>
                        Cancelling...
                      </>
                    ) : (
                      'Cancel Analysis'
                    )}
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
