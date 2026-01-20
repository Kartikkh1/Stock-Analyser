"""Configuration and initialization for the backend."""

import os
from dotenv import load_dotenv
import finnhub
from stock_analyser.utils.logger import logger

# Load environment variables
load_dotenv()

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",  # React frontend development server
]

# LLM Model Mapping
# Maps frontend LLM choice to actual model names that CrewAI expects
LLM_MODEL_MAPPING = {
    "openai": "openai/gpt-4o",           # OpenAI's latest GPT-4 model
    # NOTE: Use a concrete Anthropic model ID. Some accounts/SDKs do not support "-latest"
    # aliases and will return a 404 model_not_found.
    "anthropic": "anthropic/claude-sonnet-4",  
    "google": "gemini/gemini-2.5-pro",        # Google's Gemini model
}


def get_llm_model(llm_choice: str) -> str:
    """
    Get the actual model name from the LLM choice.
    
    Args:
        llm_choice: The LLM provider choice (e.g., "openai", "anthropic", "google")
    
    Returns:
        The actual model name to use with CrewAI
    """
    model = LLM_MODEL_MAPPING.get(llm_choice.lower())
    if not model:
        logger.warning(f"Unknown LLM choice '{llm_choice}', defaulting to OpenAI")
        model = LLM_MODEL_MAPPING["openai"]
    
    logger.info(f"LLM choice '{llm_choice}' mapped to model '{model}'")
    return model


def get_finnhub_client():
    """
    Initialize and return Finnhub client for ticker validation.
    Returns None if initialization fails.
    """
    try:
        api_key = os.getenv("FINNHUB_API_KEY")
        if api_key:
            client = finnhub.Client(api_key=api_key)
            logger.info("Finnhub client initialized for ticker validation")
            return client
        else:
            logger.warning("FINNHUB_API_KEY not found in environment")
            return None
    except Exception as e:
        logger.warning(f"Could not initialize Finnhub client: {e}")
        return None
