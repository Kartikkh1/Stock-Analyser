import React from 'react';
import TickerInput from '../TickerInput/TickerInput';
import LLMSelector from '../LLMSelector/LLMSelector';
import './AnalysisForm.css';

const AnalysisForm = ({
  onSubmit,
  error,
  isAnalyzing,
  isCancelling,
  onCancel,
  tickerProps,
  llmProps,
}) => {
  return (
    <div className="analysis-form-card card form-card">
      <h2>Generate Analysis Report</h2>
      <form onSubmit={onSubmit} className="analysis-form">
        <TickerInput
          stockTicker={tickerProps.stockTicker}
          onChange={tickerProps.onChange}
          isTickerValid={tickerProps.isTickerValid}
          tickerError={tickerProps.tickerError}
          isValidating={tickerProps.isValidating}
          companyInfo={tickerProps.companyInfo}
          disabled={isAnalyzing}
        />

        <LLMSelector
          value={llmProps.value}
          onChange={llmProps.onChange}
          disabled={isAnalyzing}
        />

        {error && (
          <div className="analysis-alert alert-error">
            <span className="analysis-alert-icon">⚠️</span>
            {error}
          </div>
        )}

        <div className="analysis-button-group">
          {!isAnalyzing ? (
            <button type="submit" className="button button-primary">
              Generate Report
            </button>
          ) : (
            <button
              type="button"
              onClick={onCancel}
              className="button button-secondary"
              disabled={isCancelling}
            >
              {isCancelling ? (
                <>
                  <span className="analysis-button-spinner"></span>
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
  );
};

export default AnalysisForm;
