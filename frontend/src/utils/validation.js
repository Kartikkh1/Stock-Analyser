import { TICKER_VALIDATION, ERROR_MESSAGES } from '../constants/config';

export const validateTickerFormat = (ticker) => {
  const trimmedTicker = ticker.trim().toUpperCase();
  
  // Empty ticker
  if (!trimmedTicker) {
    return { valid: false, error: '' };
  }
  
  // Check if it contains only letters
  if (!TICKER_VALIDATION.PATTERN.test(trimmedTicker)) {
    return { valid: false, error: ERROR_MESSAGES.TICKER_LETTERS_ONLY };
  }
  
  // Check length (most stock tickers are 1-5 characters)
  if (trimmedTicker.length < TICKER_VALIDATION.MIN_LENGTH || 
      trimmedTicker.length > TICKER_VALIDATION.MAX_LENGTH) {
    return { valid: false, error: ERROR_MESSAGES.TICKER_LENGTH };
  }
  
  return { valid: true, error: '' };
};

export const normalizeTicker = (ticker) => {
  return ticker.trim().toUpperCase();
};
