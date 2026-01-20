import { WS_BASE_URL, WS_ENDPOINTS, WEBSOCKET_CONFIG, ERROR_MESSAGES } from '../constants/config';
import { normalizeTicker } from './validation';

export const createAnalysisWebSocket = ({
  ticker,
  llmProvider,
  onMessage,
  onError,
  onClose,
  onOpen,
}) => {
  const wsUrl = `${WS_BASE_URL}${WS_ENDPOINTS.REPORT}`;
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
    
    // Send initial request
    const payload = {
      stock_ticker: normalizeTicker(ticker),
      llm_choice: llmProvider,
    };
    
    ws.send(JSON.stringify(payload));
    
    if (onOpen) {
      onOpen();
    }
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Received WebSocket message:', data);
      
      if (onMessage) {
        onMessage(data);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      if (onError) {
        onError(new Error('Failed to parse server response'));
      }
    }
  };
  
  ws.onerror = (event) => {
    console.error('WebSocket error:', event);
    
    if (onError) {
      onError(new Error(ERROR_MESSAGES.WEBSOCKET_ERROR));
    }
  };
  
  ws.onclose = (event) => {
    console.log('WebSocket closed', event);
    
    // Clear any pending cancel timeout
    if (ws.cancelTimeout) {
      clearTimeout(ws.cancelTimeout);
    }
    
    if (onClose) {
      onClose(event);
    }
  };
  
  return ws;
};

export const cancelAnalysis = (ws, onTimeout) => {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.warn('WebSocket is not open, cannot send cancel message');
    return false;
  }
  
  try {
    ws.send(JSON.stringify({ action: 'cancel' }));
    console.log('Cancel message sent to server, waiting for confirmation...');
    
    // Set safety timeout to prevent hanging
    if (onTimeout) {
      const safetyTimeout = setTimeout(() => {
        console.log('Safety timeout: forcing WebSocket close');
        onTimeout();
      }, WEBSOCKET_CONFIG.CANCEL_SAFETY_TIMEOUT);
      
      // Store timeout reference so it can be cleared later
      ws.cancelTimeout = safetyTimeout;
    }
    
    return true;
  } catch (error) {
    console.error('Error sending cancel message:', error);
    return false;
  }
};

export const closeWebSocket = (ws, sendCancel = false) => {
  if (!ws) {
    return;
  }
  
  // Clear any pending cancel timeout
  if (ws.cancelTimeout) {
    clearTimeout(ws.cancelTimeout);
  }
  
  // Send cancel message if requested and connection is open
  if (sendCancel && ws.readyState === WebSocket.OPEN) {
    try {
      ws.send(JSON.stringify({ action: 'cancel' }));
    } catch (error) {
      console.error('Error sending cancel on close:', error);
    }
  }
  
  // Close the connection
  if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
    ws.close();
  }
};
