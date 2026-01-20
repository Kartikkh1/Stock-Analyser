import os
from typing import Any
import finnhub
from crewai.tools import tool
from stock_analyser.utils.logger import logger


def _get_finnhub_client() -> finnhub.Client | None:
    """Create a Finnhub client using FINNHUB_API_KEY (or return None if missing)."""
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return None
    return finnhub.Client(api_key=api_key)


def _no_key_error() -> dict[str, Any]:
    return {"error": "FINNHUB_API_KEY not set. Finnhub tools are unavailable."}


@tool("get_real_time_quote")
def get_real_time_quote(symbol: str) -> dict[str, Any]:
    """Get a real-time quote for `symbol` using Finnhub (quote endpoint)."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        return client.quote(symbol)
    except Exception as e:
        logger.error(f"Finnhub quote error for {symbol}: {e}", exc_info=True)
        return {"error": str(e)}


@tool("get_historical_prices")
def get_historical_prices(symbol: str, resolution: str, from_ts: int, to_ts: int) -> dict[str, Any]:
    """
    Get historical OHLCV candles for `symbol` from Finnhub.

    - `resolution`: 1, 5, 15, 30, 60, D, W, M
    - `from_ts` / `to_ts`: UNIX timestamps (seconds)
    """
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        return client.stock_candles(symbol, resolution, from_ts, to_ts)
    except Exception as e:
        logger.error(f"Finnhub stock_candles error for {symbol}: {e}", exc_info=True)
        return {"error": str(e)}


@tool("get_fundamental_data")
def get_fundamental_data(symbol: str, metric_type: str = "all") -> dict[str, Any]:
    """Get company basic fundamentals for `symbol` from Finnhub (company_basic_financials)."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        return client.company_basic_financials(symbol, metric_type)
    except Exception as e:
        logger.error(f"Finnhub fundamentals error for {symbol}: {e}", exc_info=True)
        return {"error": str(e)}


@tool("get_company_news")
def get_company_news(symbol: str, from_date: str, to_date: str) -> dict[str, Any]:
    """
    Get company news for `symbol` from Finnhub.

    - `from_date` / `to_date`: YYYY-MM-DD
    """
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        return client.company_news(symbol, from_date, to_date)
    except Exception as e:
        logger.error(f"Finnhub company_news error for {symbol}: {e}", exc_info=True)
        return {"error": str(e)}


@tool("get_news_sentiment")
def get_news_sentiment(symbol: str) -> dict[str, Any]:
    """Get aggregated news sentiment for `symbol` from Finnhub (news_sentiment)."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        return client.news_sentiment(symbol)
    except Exception as e:
        logger.error(f"Finnhub news_sentiment error for {symbol}: {e}", exc_info=True)
        return {"error": str(e)}


@tool("analyst_rating")
def analyst_rating(symbol: str) -> dict[str, Any]:
    """
    Get analyst rating proxy for `symbol` from Finnhub.

    Finnhub exposes this as recommendation trends (recommendation_trends).
    """
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        return client.recommendation_trends(symbol)
    except Exception as e:
        logger.error(f"Finnhub recommendation_trends error for {symbol}: {e}", exc_info=True)
        return {"error": str(e)}


def get_finnhub_tools() -> list[Any]:
    """Return all Finnhub tools (atomic). Raises if key missing to match existing pattern."""
    if not os.getenv("FINNHUB_API_KEY"):
        raise ValueError("FINNHUB_API_KEY not provided.")
    return [
        get_real_time_quote,
        get_historical_prices,
        get_fundamental_data,
        get_company_news,
        get_news_sentiment,
        analyst_rating,
    ]
