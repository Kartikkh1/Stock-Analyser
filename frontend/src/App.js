import React from 'react';
import './App.css';
import Header from './components/Header/Header';
import AnalysisForm from './components/AnalysisForm/AnalysisForm';
import ProgressBar from './components/ProgressBar/ProgressBar';
import ReportDisplay from './components/ReportDisplay/ReportDisplay';
import { useTickerValidation } from './hooks/useTickerValidation';
import { useStockAnalysis } from './hooks/useStockAnalysis';
import { useLLMProvider } from './hooks/useLLMProvider';
import { ERROR_MESSAGES } from './constants/config';

function App() {
  // Custom hooks for state management
  const tickerValidation = useTickerValidation();
  const { llmChoice, setLlmChoice } = useLLMProvider();
  
  const {
    isAnalyzing,
    progress,
    statusMessage,
    report,
    error,
    isCancelling,
    handleSubmit: submitAnalysis,
    handleCancel,
  } = useStockAnalysis({
    ticker: tickerValidation.stockTicker,
    llmProvider: llmChoice,
  });

  // Handle form submission with validation
  const handleFormSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    if (!tickerValidation.stockTicker.trim()) {
      return;
    }

    if (!tickerValidation.isTickerValid) {
      return;
    }

    submitAnalysis();
  };

  return (
    <div className="App">
      <div className="container">
        <Header />

        <div className="content">
          <AnalysisForm
            onSubmit={handleFormSubmit}
            error={error}
            isAnalyzing={isAnalyzing}
            isCancelling={isCancelling}
            onCancel={handleCancel}
            tickerProps={{
              stockTicker: tickerValidation.stockTicker,
              onChange: tickerValidation.handleTickerChange,
              isTickerValid: tickerValidation.isTickerValid,
              tickerError: tickerValidation.tickerError,
              isValidating: tickerValidation.isValidating,
              companyInfo: tickerValidation.companyInfo,
            }}
            llmProps={{
              value: llmChoice,
              onChange: setLlmChoice,
            }}
          />

          <ProgressBar
            progress={progress}
            statusMessage={statusMessage}
            isVisible={isAnalyzing}
          />

          <ReportDisplay
            report={report}
            stockTicker={tickerValidation.stockTicker}
            llmChoice={llmChoice}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
