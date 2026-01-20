import React from 'react';
import { LLM_PROVIDER_OPTIONS } from '../../constants/config';
import './LLMSelector.css';

const LLMSelector = ({ value, onChange, disabled = false }) => {
  return (
    <div className="llm-selector-group">
      <label className="llm-selector-label">Select LLM Provider</label>
      <div className="llm-radio-group">
        {LLM_PROVIDER_OPTIONS.map((provider) => (
          <label key={provider.value} className="llm-radio-label">
            <input
              type="radio"
              name="llmChoice"
              value={provider.value}
              checked={value === provider.value}
              onChange={(e) => onChange(e.target.value)}
              disabled={disabled}
            />
            <span className="llm-radio-text">
              <strong>{provider.label}</strong>
              <small>{provider.description}</small>
            </span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default LLMSelector;
