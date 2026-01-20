import React from 'react';
import './TickerInput.css';

const TickerInput = ({
  stockTicker,
  onChange,
  isTickerValid,
  tickerError,
  isValidating,
  companyInfo,
  disabled = false,
}) => {
  return (
    <div className="ticker-input-group">
      <label htmlFor="stockTicker" className="ticker-label">
        Stock Ticker Symbol
      </label>
      <div className="ticker-input-wrapper">
        <input
          type="text"
          id="stockTicker"
          className={`ticker-input ${stockTicker && (isTickerValid ? 'ticker-input-valid' : tickerError ? 'ticker-input-invalid' : '')}`}
          value={stockTicker}
          onChange={onChange}
          placeholder="e.g., AAPL, TSLA, MSFT"
          disabled={disabled}
          maxLength={5}
          required
        />
        {stockTicker && !isValidating && (
          <span className={`ticker-validation-icon ${isTickerValid ? 'valid' : 'invalid'}`}>
            {isTickerValid ? '✓' : '✗'}
          </span>
        )}
        {isValidating && (
          <span className="ticker-validation-spinner"></span>
        )}
      </div>
      {tickerError && stockTicker && !isValidating && (
        <small className="ticker-error-hint">{tickerError}</small>
      )}
      {!tickerError && !stockTicker && (
        <small className="ticker-hint">Enter a 1-5 letter stock ticker symbol (e.g., AAPL, TSLA)</small>
      )}
      {isValidating && (
        <small className="ticker-hint">Validating ticker symbol...</small>
      )}
      {isTickerValid && companyInfo && !isValidating && (
        <div className="ticker-company-info">
          <small className="ticker-success-hint">
            ✓ Valid: <strong>{companyInfo.company_name}</strong>
          </small>
          {companyInfo.exchange && companyInfo.country && (
            <small className="ticker-info-hint">
              {companyInfo.exchange} • {companyInfo.country}
              {companyInfo.industry && ` • ${companyInfo.industry}`}
            </small>
          )}
        </div>
      )}
    </div>
  );
};

export default TickerInput;
