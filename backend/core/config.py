"""Configuration and initialization for the backend."""

import os
from dotenv import load_dotenv
import finnhub
from stock_analyser.utils.logger import logger

# Load environment variables
load_dotenv()


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


def get_cors_origins():
    """
    Get allowed CORS origins for the application.
    """
    return [
        "http://localhost",
        "http://localhost:3000",  # React frontend development server
    ]
