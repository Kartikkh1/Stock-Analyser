import os
from typing import Optional
from pydantic import PrivateAttr

import finnhub
from pydantic import Field
from crewai.tools import BaseTool

from stock_analyser.utils.logger import logger


class FinnhubAPITools(BaseTool):
    name: str = "Finnhub Financial Market Data Tool"
    description: str = (
        "Provides access to Finnhub financial market data. "
        "Capabilities include fetching historical stock price candles (OHLCV), "
        "company fundamental financial data, real-time stock quotes, "
        "company-specific news within a date range, and aggregated news sentiment "
        "for publicly traded companies. "
        "Use this tool whenever authoritative market, pricing, fundamentals, "
        "or news data is required."
    )

    # Secret – excluded from prompts, schemas, and logs
    api_key: Optional[str] = Field(default=None, exclude=True, repr=False)
    # Declare the client as a private attribute
    _finnhub_client: finnhub.Client = PrivateAttr()
    def __init__(self, api_key: str | None = None):
        super().__init__()

        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            logger.error(
                "Finnhub API key not provided. "
                "Set FINNHUB_API_KEY environment variable or pass it directly."
            )
            raise ValueError("Finnhub API key not provided.")

        self._finnhub_client = finnhub.Client(api_key=self.api_key)
        logger.info("FinnhubAPITools initialized successfully.")

    def _run(self, tool_name: str, **kwargs):
        """
        Internal dispatcher for Finnhub operations.
        This method is not exposed to the LLM.
        """
        logger.info(f"Executing Finnhub tool operation: {tool_name} with args: {kwargs}")

        if tool_name == "get_historical_prices":
            return self._get_historical_prices(**kwargs)
        elif tool_name == "get_fundamental_data":
            return self._get_fundamental_data(**kwargs)
        elif tool_name == "get_real_time_quote":
            return self._get_real_time_quote(**kwargs)
        elif tool_name == "get_company_news":
            return self._get_company_news(**kwargs)
        elif tool_name == "get_news_sentiment":
            return self._get_news_sentiment(**kwargs)

        logger.warning(f"Unknown Finnhub tool operation requested: {tool_name}")
        raise ValueError(f"Unknown tool name: {tool_name}")

    def _get_historical_prices(self, symbol: str, resolution: str, _from: int, to: int):
        """
        Fetch historical OHLCV price data for a stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., AAPL)
            resolution: Candle resolution (1, 5, 15, 30, 60, D, W, M)
            _from: UNIX timestamp for start of range
            to: UNIX timestamp for end of range
        """
        logger.debug(
            f"Fetching historical prices for {symbol} from {_from} to {to} "
            f"with resolution {resolution}"
        )
        try:
            return self._finnhub_client.stock_candles(symbol, resolution, _from, to)
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(
                f"Finnhub API error fetching historical prices for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}
        except Exception as e:
            logger.error(
                f"Unexpected error fetching historical prices for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}

    def _get_fundamental_data(self, symbol: str, metric_type: str):
        """
        Fetch fundamental financial data for a company.

        Args:
            symbol: Stock ticker symbol
            metric_type: Financial metric category
        """
        logger.debug(f"Fetching fundamental data for {symbol} ({metric_type})")
        try:
            return self._finnhub_client.company_basic_financials(symbol, metric_type)
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(
                f"Finnhub API error fetching fundamental data for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}
        except Exception as e:
            logger.error(
                f"Unexpected error fetching fundamental data for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}

    def _get_real_time_quote(self, symbol: str):
        """
        Fetch a real-time market quote for a stock symbol.
        """
        logger.debug(f"Fetching real-time quote for {symbol}")
        try:
            return self._finnhub_client.quote(symbol)
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(
                f"Finnhub API error fetching real-time quote for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}
        except Exception as e:
            logger.error(
                f"Unexpected error fetching real-time quote for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}

    def _get_company_news(self, symbol: str, _from: str, to: str):
        """
        Fetch company-related news articles within a date range.
        """
        logger.debug(f"Fetching company news for {symbol} from {_from} to {to}")
        try:
            return self._finnhub_client.company_news(symbol, _from, to)
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(
                f"Finnhub API error fetching company news for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}
        except Exception as e:
            logger.error(
                f"Unexpected error fetching company news for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}

    def _get_news_sentiment(self, symbol: str):
        """
        Fetch aggregated news sentiment for a company.
        """
        logger.debug(f"Fetching news sentiment for {symbol}")
        try:
            return self._finnhub_client.news_sentiment(symbol)
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(
                f"Finnhub API error fetching news sentiment for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}
        except Exception as e:
            logger.error(
                f"Unexpected error fetching news sentiment for {symbol}: {e}",
                exc_info=True,
            )
            return {"error": str(e)}
