import os
import re
from datetime import datetime, timedelta
from typing import Any
import finnhub
from finnhub.exceptions import FinnhubAPIException
from crewai.tools import tool
from stock_analyser.utils.logger import logger


def _get_finnhub_client() -> finnhub.Client | None:
    """Create a Finnhub client using FINNHUB_API_KEY (or return None if missing)."""
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return None
    return finnhub.Client(api_key=api_key)


def _no_key_error() -> dict[str, Any]:
    return {
        "error": "FINNHUB_API_KEY not set. DO NOT retry this tool.",
        "action": "Skip this data source and proceed with other available information.",
        "retryable": False,
        "error_type": "missing_api_key",
    }


def _extract_status_code(e: Exception) -> int | None:
    if isinstance(e, FinnhubAPIException):
        status_code = getattr(e, "status_code", None)
        if status_code is not None:
            try:
                return int(status_code)
            except (TypeError, ValueError):
                return None
    match = re.search(r"status_code:\s*(\d+)", str(e))
    if match:
        return int(match.group(1))
    return None


def _handle_error(tool_name: str, symbol: str, e: Exception) -> dict[str, Any]:
    """Return LLM-friendly error with clear instruction not to retry."""
    error_str = str(e)
    status_code = _extract_status_code(e)

    # 401/403 = access denied (premium feature or invalid permissions)
    if status_code in {401, 403}:
        return {
            "error": f"Access denied for {tool_name}. This requires a Finnhub premium subscription.",
            "symbol": symbol,
            "status_code": status_code,
            "retryable": False,
            "error_type": "access_denied",
            "action": "DO NOT retry this tool. Skip this data and continue with other sources.",
        }

    # 429 = rate limited
    if status_code == 429:
        return {
            "error": f"{tool_name} rate-limited by Finnhub.",
            "symbol": symbol,
            "status_code": status_code,
            "retryable": True,
            "error_type": "rate_limited",
            "action": "Retry later with backoff or use alternative data sources.",
        }

    # 5xx = server errors
    if status_code and 500 <= status_code < 600:
        return {
            "error": f"{tool_name} unavailable due to Finnhub server error.",
            "symbol": symbol,
            "status_code": status_code,
            "retryable": True,
            "error_type": "server_error",
            "action": "Retry later or use alternative data sources.",
        }

    # Generic error
    return {
        "error": f"{tool_name} failed: {error_str}",
        "symbol": symbol,
        "status_code": status_code,
        "retryable": False,
        "error_type": "unknown_error",
        "action": "DO NOT retry this tool with the same parameters. Try alternative data sources.",
    }


@tool("get_real_time_quote")
def get_real_time_quote(symbol: str) -> dict[str, Any]:
    """Get a real-time quote for `symbol` using Finnhub."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        q = client.quote(symbol)
        return {
            "symbol": symbol,
            "currentPrice": q.get("c"),
            "dayHigh": q.get("h"),
            "dayLow": q.get("l"),
            "openPrice": q.get("o"),
            "previousClose": q.get("pc"),
            "timestamp": q.get("t"),
        }
    except FinnhubAPIException as e:
        logger.warning(f"Finnhub quote error for {symbol}: {e}")
        return _handle_error("get_real_time_quote", symbol, e)
    except Exception as e:
        logger.error(f"Finnhub quote error for {symbol}: {e}", exc_info=True)
        return _handle_error("get_real_time_quote", symbol, e)


@tool("get_historical_prices")
def get_historical_prices(
    symbol: str,
    resolution: str,
    from_ts: int,
    to_ts: int
) -> dict[str, Any]:
    """Get summarized historical price data (min, max, avg, last close)."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        data = client.stock_candles(symbol, resolution, from_ts, to_ts)
        status = data.get("s")
        if status and status != "ok":
            return {
                "error": "No price data available",
                "symbol": symbol,
                "status": status,
                "retryable": False,
                "error_type": "no_data",
                "action": "Skip historical prices and continue with other sources.",
            }
        closes = data.get("c", [])
        if not closes:
            return {
                "error": "No price data available",
                "symbol": symbol,
                "retryable": False,
                "error_type": "no_data",
                "action": "Skip historical prices and continue with other sources.",
            }
        return {
            "symbol": symbol,
            "period": {"from": from_ts, "to": to_ts},
            "count": len(closes),
            "min_close": round(min(closes), 2),
            "max_close": round(max(closes), 2),
            "avg_close": round(sum(closes) / len(closes), 2),
            "last_close": round(closes[-1], 2),
        }
    except FinnhubAPIException as e:
        logger.warning(f"Finnhub stock_candles error for {symbol}: {e}")
        return _handle_error("get_historical_prices", symbol, e)
    except Exception as e:
        logger.error(f"Finnhub stock_candles error for {symbol}: {e}", exc_info=True)
        return _handle_error("get_historical_prices", symbol, e)


@tool("get_historical_candles")
def get_historical_candles(
    symbol: str,
    resolution: str = "D",
    days: int = 180
) -> dict[str, Any]:
    """Get historical candle data (Date, Close) for the last N days."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        to_ts = int(datetime.utcnow().timestamp())
        from_ts = int((datetime.utcnow() - timedelta(days=days)).timestamp())
        data = client.stock_candles(symbol, resolution, from_ts, to_ts)
        status = data.get("s")
        if status and status != "ok":
            return {
                "error": "No candle data available",
                "symbol": symbol,
                "status": status,
                "retryable": False,
                "error_type": "no_data",
                "action": "Skip candle data and continue with other sources.",
            }
        timestamps = data.get("t", [])
        closes = data.get("c", [])
        if not timestamps or not closes:
            return {
                "error": "No candle data available",
                "symbol": symbol,
                "retryable": False,
                "error_type": "no_data",
                "action": "Skip candle data and continue with other sources.",
            }
        candles = [
            {
                "Date": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d"),
                "Close": close,
            }
            for ts, close in zip(timestamps, closes)
        ]
        return {
            "symbol": symbol,
            "resolution": resolution,
            "count": len(candles),
            "candles": candles,
        }
    except FinnhubAPIException as e:
        logger.warning(f"Finnhub stock_candles error for {symbol}: {e}")
        return _handle_error("get_historical_candles", symbol, e)
    except Exception as e:
        logger.error(f"Finnhub stock_candles error for {symbol}: {e}", exc_info=True)
        return _handle_error("get_historical_candles", symbol, e)


@tool("get_fundamental_data")
def get_fundamental_data(symbol: str, metric_type: str = "all") -> dict[str, Any]:
    """Get key financial metrics for `symbol` (PE, EPS, market cap, 52-week range, etc.)."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        data = client.company_basic_financials(symbol, metric_type)
        metrics = data.get("metric", {})
        # Extract only the most important metrics to reduce token usage
        key_metrics = {
            "symbol": symbol,
            "peRatio": metrics.get("peNormalizedAnnual"),
            "eps": metrics.get("epsNormalizedAnnual"),
            "marketCap": metrics.get("marketCapitalization"),
            "52WeekHigh": metrics.get("52WeekHigh"),
            "52WeekLow": metrics.get("52WeekLow"),
            "dividendYield": metrics.get("dividendYieldIndicatedAnnual"),
            "beta": metrics.get("beta"),
            "priceToBook": metrics.get("pbAnnual"),
            "priceToSales": metrics.get("psAnnual"),
            "revenuePerShare": metrics.get("revenuePerShareAnnual"),
            "roe": metrics.get("roeRfy"),
            "debtToEquity": metrics.get("totalDebt/totalEquityAnnual"),
        }
        # Remove None values to keep response clean
        return {k: v for k, v in key_metrics.items() if v is not None}
    except FinnhubAPIException as e:
        logger.warning(f"Finnhub fundamentals error for {symbol}: {e}")
        return _handle_error("get_fundamental_data", symbol, e)
    except Exception as e:
        logger.error(f"Finnhub fundamentals error for {symbol}: {e}", exc_info=True)
        return _handle_error("get_fundamental_data", symbol, e)


@tool("get_company_news")
def get_company_news(symbol: str, from_date: str, to_date: str) -> dict[str, Any]:
    """Get recent company news for `symbol` (max 5 articles, headline + summary only)."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        news = client.company_news(symbol, from_date, to_date)
        # Limit to 5 articles, extract only essential fields
        summarized = [
            {
                "headline": article.get("headline"),
                "summary": article.get("summary", "")[:200],  # Truncate long summaries
                "source": article.get("source"),
                "datetime": article.get("datetime"),
            }
            for article in news[:5]
        ]
        return {"symbol": symbol, "count": len(news), "articles": summarized}
    except FinnhubAPIException as e:
        logger.warning(f"Finnhub company_news error for {symbol}: {e}")
        return _handle_error("get_company_news", symbol, e)
    except Exception as e:
        logger.error(f"Finnhub company_news error for {symbol}: {e}", exc_info=True)
        return _handle_error("get_company_news", symbol, e)


@tool("get_news_sentiment")
def get_news_sentiment(symbol: str) -> dict[str, Any]:
    """Get aggregated news sentiment scores for `symbol`."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        data = client.news_sentiment(symbol)
        sentiment = data.get("sentiment", {})
        buzz = data.get("buzz", {})
        return {
            "symbol": symbol,
            "companyName": data.get("companyNewsScore"),
            "sentiment": {
                "bullishPercent": sentiment.get("bullishPercent"),
                "bearishPercent": sentiment.get("bearishPercent"),
                "score": sentiment.get("score"),
            },
            "buzz": {
                "articlesInLastWeek": buzz.get("articlesInLastWeek"),
                "buzz": buzz.get("buzz"),
            },
            "sectorAverageBullishPercent": data.get("sectorAverageBullishPercent"),
        }
    except FinnhubAPIException as e:
        logger.warning(f"Finnhub news_sentiment error for {symbol}: {e}")
        return _handle_error("get_news_sentiment", symbol, e)
    except Exception as e:
        logger.error(f"Finnhub news_sentiment error for {symbol}: {e}", exc_info=True)
        return _handle_error("get_news_sentiment", symbol, e)


@tool("analyst_rating")
def analyst_rating(symbol: str) -> dict[str, Any]:
    """Get analyst recommendation trends for `symbol` (last 3 months)."""
    client = _get_finnhub_client()
    if not client:
        return _no_key_error()
    try:
        trends = client.recommendation_trends(symbol)
        # Limit to last 3 months of data
        recent = trends[:6] if trends else []
        return {"symbol": symbol, "recommendations": recent}
    except FinnhubAPIException as e:
        logger.warning(f"Finnhub recommendation_trends error for {symbol}: {e}")
        return _handle_error("analyst_rating", symbol, e)
    except Exception as e:
        logger.error(f"Finnhub recommendation_trends error for {symbol}: {e}", exc_info=True)
        return _handle_error("analyst_rating", symbol, e)


def get_finnhub_tools() -> list[Any]:
    """Return all Finnhub tools (atomic). Raises if key missing to match existing pattern."""
    if not os.getenv("FINNHUB_API_KEY"):
        raise ValueError("FINNHUB_API_KEY not provided.")
    return [
        get_real_time_quote,
        get_historical_prices,
        get_historical_candles,
        get_fundamental_data,
        get_company_news,
        get_news_sentiment,
        analyst_rating,
    ]
