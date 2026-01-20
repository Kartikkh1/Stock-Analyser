import { useState, useRef, useEffect } from 'react';
import { validateTickerFormat } from '../utils/validation';
import { validateTickerAPI } from '../utils/api';
import { TICKER_VALIDATION } from '../constants/config';

/**
 * Custom hook for ticker validation with debounced API calls
 * 
 * Manages ticker validation state and provides validation logic
 * with both client-side format validation and server-side API validation.
 * 
 * @returns {Object} Ticker validation state and handlers
 */
export const useTickerValidation = () => {
  const [stockTicker, setStockTicker] = useState('');
  const [isTickerValid, setIsTickerValid] = useState(false);
  const [tickerError, setTickerError] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [companyInfo, setCompanyInfo] = useState(null);
  
  const validationTimeoutRef = useRef(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }
    };
  }, []);

  // Validate ticker with backend API
  const validateWithAPI = async (ticker) => {
    if (!ticker.trim()) {
      return;
    }
    
    setIsValidating(true);
    
    try {
      const result = await validateTickerAPI(ticker);
      
      if (result.valid) {
        setIsTickerValid(true);
        setTickerError('');
        setCompanyInfo({
          company_name: result.companyName,
          exchange: result.exchange,
          country: result.country,
          industry: result.industry,
        });
      } else {
        setIsTickerValid(false);
        setTickerError(result.message);
        setCompanyInfo(null);
      }
    } catch (error) {
      console.error('Ticker validation error:', error);
      setTickerError(error.message);
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
    
    // Reset company info
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
      validateWithAPI(value);
    }, TICKER_VALIDATION.DEBOUNCE_DELAY);
  };

  return {
    stockTicker,
    setStockTicker,
    isTickerValid,
    tickerError,
    isValidating,
    companyInfo,
    handleTickerChange,
  };
};
