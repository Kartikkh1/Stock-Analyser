import { API_BASE_URL, API_ENDPOINTS, ERROR_MESSAGES } from '../constants/config';
import { normalizeTicker } from './validation';

export const validateTickerAPI = async (ticker) => {
  const normalizedTicker = normalizeTicker(ticker);
  
  if (!normalizedTicker) {
    throw new Error('Ticker cannot be empty');
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.VALIDATE_TICKER}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ticker: normalizedTicker }),
    });
    
    const data = await response.json();
    
    return {
      valid: data.valid || false,
      message: data.message || (data.valid ? '' : ERROR_MESSAGES.TICKER_NOT_FOUND),
      companyName: data.company_name,
      exchange: data.exchange,
      country: data.country,
      industry: data.industry,
    };
  } catch (error) {
    console.error('Ticker validation API error:', error);
    throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
  }
};

export const apiFetch = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
};
