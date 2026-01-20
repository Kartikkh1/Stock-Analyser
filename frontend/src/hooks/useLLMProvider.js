import { useState } from 'react';

export const useLLMProvider = () => {
  const [llmChoice, setLlmChoice] = useState('openai');

  return {
    llmChoice,
    setLlmChoice
  };
};
