"""Ticker validation API endpoint."""

from fastapi import APIRouter, HTTPException

from backend.models import TickerValidationRequest
from backend.core import get_finnhub_client
from stock_analyser.utils.logger import logger

router = APIRouter()

# Initialize Finnhub client
finnhub_client = get_finnhub_client()


@router.post("/validate-ticker")
async def validate_ticker(request: TickerValidationRequest):
    """
    Validate if a stock ticker symbol exists in the market.
    Returns ticker information if valid, or error if invalid.
    
    Args:
        request: TickerValidationRequest with ticker symbol
        
    Returns:
        dict: Validation result with company information
    """
    ticker = request.ticker.upper().strip()
    
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol is required")
    
    if not finnhub_client:
        # If Finnhub is not available, do basic format validation only
        return {
            "valid": True,
            "ticker": ticker,
            "message": "Format validation only (API not available)",
            "company_name": None
        }
    
    try:
        # Try to get company profile to validate ticker exists
        profile = finnhub_client.company_profile2(symbol=ticker)
        
        # Check if we got valid data back
        if profile and profile.get('ticker'):
            return {
                "valid": True,
                "ticker": ticker,
                "company_name": profile.get('name', 'Unknown'),
                "country": profile.get('country', 'Unknown'),
                "exchange": profile.get('exchange', 'Unknown'),
                "industry": profile.get('finnhubIndustry', 'Unknown')
            }
        else:
            # Empty response means ticker doesn't exist
            return {
                "valid": False,
                "ticker": ticker,
                "message": "Ticker symbol not found"
            }
            
    except Exception as e:
        logger.error(f"Error validating ticker {ticker}: {e}")
        # If there's an error, assume ticker might not exist
        return {
            "valid": False,
            "ticker": ticker,
            "message": "Ticker symbol not found or API error"
        }
