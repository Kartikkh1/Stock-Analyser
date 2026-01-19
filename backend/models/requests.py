"""Request models for the API."""

from pydantic import BaseModel


class TickerValidationRequest(BaseModel):
    """Request model for ticker validation."""
    ticker: str
