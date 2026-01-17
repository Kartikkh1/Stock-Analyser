import os
from crewai.tools import BaseTool
import finnhub
from finnhub import Client, exceptions
from stock_analyser.utils.logger import logger

class FinnhubAPITools(BaseTool):
    name: str = "Finnhub API Tools"
    description: str = "A collection of tools to interact with the Finnhub API for financial data."

    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            logger.error("Finnhub API key not provided. Set FINNHUB_API_KEY environment variable or pass it directly.")
            raise ValueError("Finnhub API key not provided. Set FINNHUB_API_KEY environment variable or pass it directly.")
        self.finnhub_client = finnhub.Client(api_key=self.api_key)
        logger.info("FinnhubAPITools initialized.")

    def _run(self, tool_name: str, **kwargs):
        logger.info(f"Executing Finnhub tool: {tool_name} with args: {kwargs}")
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
        else:
            logger.warning(f"Unknown Finnhub tool name: {tool_name}")
            raise ValueError(f"Unknown tool name: {tool_name}")

    def _get_historical_prices(self, symbol: str, resolution: str, _from: int, to: int):
        """
        Fetches historical prices for a given symbol.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').
            resolution (str): Supported resolutions: '1', '5', '15', '30', '60', 'D', 'W', 'M'.
            _from (int): UNIX timestamp for the start date.
            to (int): UNIX timestamp for the end date.

        Returns:
            dict: Historical price data.
        """
        logger.debug(f"Fetching historical prices for {symbol} from {_from} to {to} with resolution {resolution}")
        try:
            data = self.finnhub_client.stock_candles(symbol, resolution, _from, to)
            logger.debug(f"Successfully fetched historical prices for {symbol}.")
            return data
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(f"Finnhub API Error fetching historical prices for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching historical prices for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}

    def _get_fundamental_data(self, symbol: str, metric_type: str):
        """
        Fetches fundamental data for a given symbol.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').
            metric_type (str): Metric type (e.g., 'all', 'incomeStatement', 'balanceSheet', 'cashflowStatement').

        Returns:
            dict: Fundamental data.
        """
        logger.debug(f"Fetching fundamental data for {symbol} of type {metric_type}")
        try:
            data = self.finnhub_client.company_basic_financials(symbol, metric_type)
            logger.debug(f"Successfully fetched fundamental data for {symbol}.")
            return data
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(f"Finnhub API Error fetching fundamental data for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching fundamental data for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}

    def _get_real_time_quote(self, symbol: str):
        """
        Fetches real-time quote for a given symbol.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').

        Returns:
            dict: Real-time quote data.
        """
        logger.debug(f"Fetching real-time quote for {symbol}")
        try:
            data = self.finnhub_client.quote(symbol)
            logger.debug(f"Successfully fetched real-time quote for {symbol}.")
            return data
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(f"Finnhub API Error fetching real-time quote for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching real-time quote for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}

    def _get_company_news(self, symbol: str, _from: str, to: str):
        """
        Fetches company news for a given symbol within a date range.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').
            _from (str): Start date in 'YYYY-MM-DD' format.
            to (str): End date in 'YYYY-MM-DD' format.

        Returns:
            list: List of news articles.
        """
        logger.debug(f"Fetching company news for {symbol} from {_from} to {to}")
        try:
            data = self.finnhub_client.company_news(symbol, _from, to)
            logger.debug(f"Successfully fetched company news for {symbol}.")
            return data
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(f"Finnhub API Error fetching company news for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching company news for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}

    def _get_news_sentiment(self, symbol: str):
        """
        Fetches news sentiment for a given symbol.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').

        Returns:
            dict: News sentiment data.
        """
        logger.debug(f"Fetching news sentiment for {symbol}")
        try:
            data = self.finnhub_client.news_sentiment(symbol)
            logger.debug(f"Successfully fetched news sentiment for {symbol}.")
            return data
        except finnhub.exceptions.FinnhubAPIException as e:
            logger.error(f"Finnhub API Error fetching news sentiment for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching news sentiment for {symbol}: {e}", exc_info=True)
            return {"error": str(e)}
