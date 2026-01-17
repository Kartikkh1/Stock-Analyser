import os
from crewai_tools import BaseTool
import finnhub
from finnhub import Client, exceptions

class FinnhubAPITools(BaseTool):
    name: str = "Finnhub API Tools"
    description: str = "A collection of tools to interact with the Finnhub API for financial data."

    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            raise ValueError("Finnhub API key not provided. Set FINNHUB_API_KEY environment variable or pass it directly.")
        self.finnhub_client = finnhub.Client(api_key=self.api_key)

    def _run(self, tool_name: str, **kwargs):
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
        try:
            return self.finnhub_client.stock_candles(symbol, resolution, _from, to)
        except finnhub.exceptions.FinnhubAPIException as e:
            print(f"Finnhub API Error fetching historical prices for {symbol}: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred fetching historical prices for {symbol}: {e}")
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
        try:
            return self.finnhub_client.company_basic_financials(symbol, metric_type)
        except finnhub.exceptions.FinnhubAPIException as e:
            print(f"Finnhub API Error fetching fundamental data for {symbol}: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred fetching fundamental data for {symbol}: {e}")
            return {"error": str(e)}

    def _get_real_time_quote(self, symbol: str):
        """
        Fetches real-time quote for a given symbol.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').

        Returns:
            dict: Real-time quote data.
        """
        try:
            return self.finnhub_client.quote(symbol)
        except finnhub.exceptions.FinnhubAPIException as e:
            print(f"Finnhub API Error fetching real-time quote for {symbol}: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred fetching real-time quote for {symbol}: {e}")
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
        try:
            return self.finnhub_client.company_news(symbol, _from, to)
        except finnhub.exceptions.FinnhubAPIException as e:
            print(f"Finnhub API Error fetching company news for {symbol}: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred fetching company news for {symbol}: {e}")
            return {"error": str(e)}

    def _get_news_sentiment(self, symbol: str):
        """
        Fetches news sentiment for a given symbol.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').

        Returns:
            dict: News sentiment data.
        """
        try:
            return self.finnhub_client.news_sentiment(symbol)
        except finnhub.exceptions.FinnhubAPIException as e:
            print(f"Finnhub API Error fetching news sentiment for {symbol}: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred fetching news sentiment for {symbol}: {e}")
            return {"error": str(e)}
