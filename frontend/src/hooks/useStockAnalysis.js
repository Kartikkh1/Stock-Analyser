import { useState, useRef, useEffect } from 'react';
import { createAnalysisWebSocket, cancelAnalysis, closeWebSocket } from '../utils/websocket';
import { ERROR_MESSAGES } from '../constants/config';

/**
 * Custom hook for stock analysis with WebSocket connection management
 * 
 * Manages the analysis lifecycle including WebSocket connection,
 * progress tracking, cancellation, and cleanup.
 * 
 * @param {Object} options - Hook configuration
 * @param {string} options.ticker - Stock ticker symbol
 * @param {string} options.llmProvider - LLM provider choice
 * @returns {Object} Analysis state and handlers
 */
export const useStockAnalysis = ({ ticker, llmProvider }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [report, setReport] = useState('');
  const [error, setError] = useState('');
  const [isCancelling, setIsCancelling] = useState(false);
  
  const wsRef = useRef(null);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        closeWebSocket(wsRef.current, true);
      }
    };
  }, []);

  // Handle WebSocket messages
  const handleMessage = (data) => {
    if (data.error) {
      setError(data.error);
      setIsAnalyzing(false);
      if (wsRef.current) {
        wsRef.current.close();
      }
      return;
    }

    if (data.status) {
      setStatusMessage(data.message || '');
      setProgress(data.progress || 0);

      if (data.status === 'completed') {
        setReport(data.report || '');
        setIsAnalyzing(false);
        if (wsRef.current) {
          wsRef.current.close();
        }
      } else if (data.status === 'error') {
        setError(data.message || ERROR_MESSAGES.ANALYSIS_ERROR);
        setIsAnalyzing(false);
        if (wsRef.current) {
          wsRef.current.close();
        }
      } else if (data.status === 'cancelled') {
        console.log('Received cancellation confirmation from server');
        setStatusMessage('Analysis cancelled successfully');
        setIsAnalyzing(false);
        setIsCancelling(false);
        setProgress(0);
        
        // Clear the safety timeout since we got proper confirmation
        if (wsRef.current && wsRef.current.cancelTimeout) {
          clearTimeout(wsRef.current.cancelTimeout);
        }
        
        // Now close the WebSocket after receiving confirmation
        if (wsRef.current) {
          wsRef.current.close();
        }
      }
    }
  };

  // Handle WebSocket errors
  const handleError = (errorObj) => {
    console.error('WebSocket error:', errorObj);
    setError(errorObj.message || ERROR_MESSAGES.WEBSOCKET_ERROR);
    setIsAnalyzing(false);
  };

  // Handle WebSocket close
  const handleClose = (event) => {
    console.log('WebSocket closed', event);
  };

  // Handle WebSocket open
  const handleOpen = () => {
    console.log('WebSocket connected and request sent');
  };

  // Submit analysis
  const handleSubmit = (e) => {
    if (e) {
      e.preventDefault();
    }
    
    // Validation
    if (!ticker.trim()) {
      setError(ERROR_MESSAGES.EMPTY_TICKER);
      return;
    }

    // Reset states
    setError('');
    setReport('');
    setProgress(0);
    setStatusMessage('Connecting to server...');
    setIsAnalyzing(true);

    // Create WebSocket connection
    const ws = createAnalysisWebSocket({
      ticker,
      llmProvider,
      onMessage: handleMessage,
      onError: handleError,
      onClose: handleClose,
      onOpen: handleOpen,
    });
    
    wsRef.current = ws;
  };

  // Cancel analysis
  const handleCancel = () => {
    setIsCancelling(true);
    setStatusMessage('Cancelling analysis...');
    
    const cancelSuccess = cancelAnalysis(
      wsRef.current,
      () => {
        // Safety timeout callback
        console.log('Safety timeout: forcing WebSocket close');
        if (wsRef.current) {
          wsRef.current.close();
        }
        setIsCancelling(false);
        setIsAnalyzing(false);
        setProgress(0);
      }
    );
    
    if (!cancelSuccess) {
      // If cancel failed, reset states immediately
      setIsCancelling(false);
      setIsAnalyzing(false);
      setProgress(0);
    }
  };

  return {
    isAnalyzing,
    progress,
    statusMessage,
    report,
    error,
    isCancelling,
    handleSubmit,
    handleCancel,
  };
};
