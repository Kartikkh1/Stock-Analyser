import json
import os
from datetime import datetime, timedelta
from typing import Any
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from crewai.tools import tool
from stock_analyser.utils.logger import logger


BASE_URL = "https://www.alphavantage.co/query"


def _get_api_key() -> str | None:
    return os.getenv("ALPHAVANTAGE_API_KEY")


def _no_key_error() -> dict[str, Any]:
    return {
        "error": "ALPHAVANTAGE_API_KEY not set. DO NOT retry this tool.",
        "action": "Skip this data source and proceed with other available information.",
        "retryable": False,
        "error_type": "missing_api_key",
    }


def _request(params: dict[str, Any]) -> dict[str, Any]:
    api_key = _get_api_key()
    if not api_key:
        return _no_key_error()
    params["apikey"] = api_key
    url = f"{BASE_URL}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=20) as response:
            raw = response.read().decode("utf-8")
        data = json.loads(raw)
    except (HTTPError, URLError) as e:
        logger.warning(f"Alpha Vantage request error: {e}")
        return {
            "error": f"Alpha Vantage request failed: {e}",
            "retryable": True,
            "error_type": "request_failed",
            "action": "Retry later or use alternative data sources.",
        }
    except Exception as e:
        logger.error(f"Alpha Vantage request error: {e}", exc_info=True)
        return {
            "error": f"Alpha Vantage request failed: {e}",
            "retryable": True,
            "error_type": "request_failed",
            "action": "Retry later or use alternative data sources.",
        }

    if isinstance(data, dict):
        if "Note" in data:
            return {
                "error": "Alpha Vantage rate-limited.",
                "retryable": True,
                "error_type": "rate_limited",
                "action": "Retry later with backoff or use alternative data sources.",
            }
        if "Error Message" in data:
            return {
                "error": f"Alpha Vantage error: {data.get('Error Message')}",
                "retryable": False,
                "error_type": "invalid_request",
                "action": "Check parameters or use alternative data sources.",
            }
    return data


@tool("get_av_news_sentiment")
def get_av_news_sentiment(symbol: str) -> dict[str, Any]:
    """Get news sentiment for `symbol` using Alpha Vantage."""
    data = _request({"function": "NEWS_SENTIMENT", "tickers": symbol})
    if "error" in data:
        return data

    feed = data.get("feed", [])
    if not feed:
        return {
            "error": "No sentiment data available",
            "symbol": symbol,
            "retryable": False,
            "error_type": "no_data",
            "action": "Skip sentiment data and continue with other sources.",
        }

    summarized = []
    for item in feed[:5]:
        summarized.append(
            {
                "title": item.get("title"),
                "summary": item.get("summary", "")[:200],
                "source": item.get("source"),
                "time_published": item.get("time_published"),
                "overall_sentiment_score": item.get("overall_sentiment_score"),
                "overall_sentiment_label": item.get("overall_sentiment_label"),
            }
        )

    return {
        "symbol": symbol,
        "overall_sentiment_score": data.get("overall_sentiment_score"),
        "overall_sentiment_label": data.get("overall_sentiment_label"),
        "articles": summarized,
    }


@tool("get_av_historical_candles")
def get_av_historical_candles(symbol: str, days: int = 180) -> dict[str, Any]:
    """Get daily candle data (Date, Close) for the last N days using Alpha Vantage."""
    data = _request(
        {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
        }
    )
    if "error" in data:
        return data

    series = data.get("Time Series (Daily)", {})
    if not series:
        return {
            "error": "No candle data available",
            "symbol": symbol,
            "retryable": False,
            "error_type": "no_data",
            "action": "Skip candle data and continue with other sources.",
        }

    cutoff_date = datetime.utcnow().date() - timedelta(days=days)
    candles = []
    for date_str, values in series.items():
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if date_obj < cutoff_date:
            continue
        close_value = values.get("4. close")
        if close_value is None:
            continue
        try:
            close_float = float(close_value)
        except (TypeError, ValueError):
            continue
        candles.append({"Date": date_str, "Close": close_float})

    candles.sort(key=lambda x: x["Date"])
    if not candles:
        return {
            "error": "No candle data available for requested range",
            "symbol": symbol,
            "retryable": False,
            "error_type": "no_data",
            "action": "Skip candle data and continue with other sources.",
        }

    return {
        "symbol": symbol,
        "count": len(candles),
        "candles": candles,
    }


@tool("get_av_company_overview")
def get_av_company_overview(symbol: str) -> dict[str, Any]:
    """Get company overview and key ratios for `symbol` using Alpha Vantage."""
    data = _request({"function": "OVERVIEW", "symbol": symbol})
    if "error" in data:
        return data
    if not data or not data.get("Symbol"):
        return {
            "error": "No company overview data available",
            "symbol": symbol,
            "retryable": False,
            "error_type": "no_data",
            "action": "Skip overview data and continue with other sources.",
        }

    key_metrics = {
        "symbol": data.get("Symbol", symbol),
        "name": data.get("Name"),
        "marketCap": data.get("MarketCapitalization"),
        "peRatio": data.get("PERatio"),
        "eps": data.get("EPS"),
        "dividendYield": data.get("DividendYield"),
        "52WeekHigh": data.get("52WeekHigh"),
        "52WeekLow": data.get("52WeekLow"),
        "beta": data.get("Beta"),
        "priceToBook": data.get("PriceToBookRatio"),
        "profitMargin": data.get("ProfitMargin"),
        "operatingMargin": data.get("OperatingMarginTTM"),
        "roe": data.get("ReturnOnEquityTTM"),
        "revenueTTM": data.get("RevenueTTM"),
        "ebitda": data.get("EBITDA"),
        "analystTargetPrice": data.get("AnalystTargetPrice"),
    }
    return {k: v for k, v in key_metrics.items() if v not in (None, "")}


@tool("get_av_financial_statements")
def get_av_financial_statements(symbol: str) -> dict[str, Any]:
    """Get last 2 years of income, balance sheet, and cash flow statements."""
    income = _request({"function": "INCOME_STATEMENT", "symbol": symbol})
    balance = _request({"function": "BALANCE_SHEET", "symbol": symbol})
    cash_flow = _request({"function": "CASH_FLOW", "symbol": symbol})

    if "error" in income and "error" in balance and "error" in cash_flow:
        return income

    errors = []
    income_reports = []
    balance_reports = []
    cash_reports = []

    if "error" in income:
        errors.append({"source": "income_statement", "error": income.get("error")})
    else:
        income_reports = income.get("annualReports", [])[:2]

    if "error" in balance:
        errors.append({"source": "balance_sheet", "error": balance.get("error")})
    else:
        balance_reports = balance.get("annualReports", [])[:2]

    if "error" in cash_flow:
        errors.append({"source": "cash_flow", "error": cash_flow.get("error")})
    else:
        cash_reports = cash_flow.get("annualReports", [])[:2]

    if not income_reports and not balance_reports and not cash_reports:
        return {
            "error": "No financial statement data available",
            "symbol": symbol,
            "retryable": False,
            "error_type": "no_data",
            "action": "Skip statements and continue with other sources.",
        }

    result: dict[str, Any] = {
        "symbol": symbol,
        "income_statement": income_reports,
        "balance_sheet": balance_reports,
        "cash_flow": cash_reports,
    }
    if errors:
        result["errors"] = errors
    return result


def get_alpha_vantage_tools() -> list[Any]:
    """Return Alpha Vantage tools. Raises if key missing to match existing pattern."""
    if not os.getenv("ALPHAVANTAGE_API_KEY"):
        raise ValueError("ALPHAVANTAGE_API_KEY not provided.")
    return [
        get_av_news_sentiment,
        get_av_historical_candles,
        get_av_company_overview,
        get_av_financial_statements,
    ]
