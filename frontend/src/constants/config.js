/**
 * Application Configuration Constants
 * 
 * Centralized configuration values for API endpoints,
 * WebSocket connections, and validation parameters.
 */

// API Configuration
export const API_BASE_URL = 'http://localhost:8000';
export const WS_BASE_URL = 'ws://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  VALIDATE_TICKER: '/api/validate-ticker',
};

// WebSocket Endpoints
export const WS_ENDPOINTS = {
  REPORT: '/ws/report',
};

// LLM Provider Options
export const LLM_PROVIDERS = {
  OPENAI: 'openai',
  ANTHROPIC: 'anthropic',
  GEMINI: 'gemini',
};

export const LLM_PROVIDER_OPTIONS = [
  {
    value: LLM_PROVIDERS.OPENAI,
    label: 'OpenAI',
    description: 'GPT-4 powered analysis',
  },
  {
    value: LLM_PROVIDERS.ANTHROPIC,
    label: 'Anthropic',
    description: 'Claude powered analysis',
  },
  {
    value: LLM_PROVIDERS.GEMINI,
    label: 'Google Gemini',
    description: 'Gemini powered analysis',
  },
];

// Validation Constants
export const TICKER_VALIDATION = {
  MIN_LENGTH: 1,
  MAX_LENGTH: 5,
  PATTERN: /^[A-Z]+$/,
  DEBOUNCE_DELAY: 500, // milliseconds
};

// WebSocket Configuration
export const WEBSOCKET_CONFIG = {
  CANCEL_SAFETY_TIMEOUT: 3000, // milliseconds
};

// Error Messages
export const ERROR_MESSAGES = {
  EMPTY_TICKER: 'Please enter a stock ticker',
  INVALID_TICKER: 'Please enter a valid stock ticker symbol',
  TICKER_LETTERS_ONLY: 'Ticker should contain only letters',
  TICKER_LENGTH: `Ticker should be ${TICKER_VALIDATION.MIN_LENGTH}-${TICKER_VALIDATION.MAX_LENGTH} characters long`,
  TICKER_NOT_FOUND: 'Ticker symbol not found',
  NETWORK_ERROR: 'Unable to verify ticker. Please check your connection.',
  WEBSOCKET_ERROR: 'Connection error. Please ensure the backend server is running.',
  ANALYSIS_ERROR: 'An error occurred during analysis',
};
