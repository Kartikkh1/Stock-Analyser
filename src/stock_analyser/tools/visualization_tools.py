import base64
import io
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import talib
from crewai.tools import BaseTool
from stock_analyser.utils.logger import logger

import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

class VisualizationTools(BaseTool):
    name: str = "Visualization Tools"
    description: str = "Tools for generating various stock-related plots."

    def _run(self, tool_name: str, **kwargs):
        if tool_name == "plot_stock_prices":
            return self.plot_stock_prices(**kwargs)
        elif tool_name == "plot_macd":
            return self.plot_macd(**kwargs)
        elif tool_name == "plot_rsi":
            return self.plot_rsi(**kwargs)
        else:
            raise ValueError(f"Unknown Visualization tool name: {tool_name}")

    def _to_dataframe(self, data: Any) -> pd.DataFrame:
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        elif isinstance(data, dict):
            if "candles" in data:
                df = pd.DataFrame(data.get("candles", []))
            elif "t" in data and "c" in data:
                df = pd.DataFrame({
                    "Date": data.get("t", []),
                    "Close": data.get("c", []),
                })
            else:
                df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data)

        if df.empty:
            return df

        rename_map: dict[str, str] = {}
        for col in df.columns:
            lower = str(col).lower()
            if lower == "date":
                rename_map[col] = "Date"
            elif lower == "close":
                rename_map[col] = "Close"
            elif lower in {"macd", "macd_line"}:
                rename_map[col] = "MACD"
            elif lower in {"signal_line", "signal", "macd_signal"}:
                rename_map[col] = "Signal_Line"
            elif lower in {"histogram", "macd_hist", "macd_histogram"}:
                rename_map[col] = "Histogram"
            elif lower == "rsi":
                rename_map[col] = "RSI"
        if rename_map:
            df = df.rename(columns=rename_map)

        if "Signal_Line" not in df.columns and "MACD_Signal" in df.columns:
            df["Signal_Line"] = df["MACD_Signal"]
        if "Histogram" not in df.columns and "MACD_Hist" in df.columns:
            df["Histogram"] = df["MACD_Hist"]

        if "Date" in df.columns:
            if pd.api.types.is_numeric_dtype(df["Date"]):
                df["Date"] = pd.to_datetime(df["Date"], unit="s", errors="coerce")
            else:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"]).sort_values("Date")

        return df

    def plot_stock_prices(self, historical_data: pd.DataFrame, ticker: str) -> str:
        """
        Generates a line plot of historical stock prices.

        Args:
            historical_data: DataFrame with 'Date' and 'Close' columns.
            ticker: Stock ticker symbol.

        Returns:
            A base64 encoded string of the plot image.
        """
        logger.debug(f"Attempting to plot stock prices for {ticker}.")
        try:
            df = self._to_dataframe(historical_data)
            if df.empty or "Date" not in df.columns or "Close" not in df.columns:
                return "Error: Missing data for plotting stock prices. Ensure 'Date' and 'Close' are available."

            plt.figure(figsize=(10, 6))
            plt.plot(df['Date'], df['Close'], marker='o', linestyle='-')
            plt.title(f'{ticker} Stock Price Trend')
            plt.xlabel('Date')
            plt.ylabel('Close Price')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.read()).decode('utf-8')
            plt.close()
            logger.debug(f"Successfully plotted stock prices for {ticker}.")
            return img_str
        except KeyError as e:
            logger.error(f"Error plotting stock prices: Missing column {e}. Ensure 'Date' and 'Close' columns exist.", exc_info=True)
            return f"Error: Missing data for plotting stock prices: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during plotting stock prices for {ticker}: {e}", exc_info=True)
            return f"Error: An unexpected error occurred during plotting stock prices for {ticker}: {e}"

    def plot_macd(self, data: pd.DataFrame, ticker: str) -> str:
        """
        Generates a plot of MACD and Signal Line.

        Args:
            data: DataFrame with 'Date', 'MACD', and 'Signal_Line' columns.
            ticker: Stock ticker symbol.

        Returns:
            A base64 encoded string of the plot image.
        """
        logger.debug(f"Attempting to plot MACD for {ticker}.")
        try:
            df = self._to_dataframe(data)
            if df.empty or "Date" not in df.columns:
                return "Error: Missing data for plotting MACD. Ensure 'Date' and 'Close' are available."

            if {"MACD", "Signal_Line", "Histogram"}.issubset(df.columns):
                plot_df = df
            else:
                if "Close" not in df.columns:
                    return "Error: Missing 'Close' data for MACD calculation."
                macd, macd_signal, macd_hist = talib.MACD(df["Close"])
                plot_df = df.copy()
                plot_df["MACD"] = macd
                plot_df["Signal_Line"] = macd_signal
                plot_df["Histogram"] = macd_hist
                logger.debug("Computed MACD from Close prices for plotting.")

            plot_df = plot_df.dropna(subset=["MACD", "Signal_Line", "Histogram"])
            if plot_df.empty:
                return "Error: Not enough data points to plot MACD."

            plt.figure(figsize=(10, 6))
            plt.plot(plot_df['Date'], plot_df['MACD'], label='MACD', color='blue')
            plt.plot(plot_df['Date'], plot_df['Signal_Line'], label='Signal Line', color='red')
            plt.bar(plot_df['Date'], plot_df['Histogram'], label='Histogram', color='gray', alpha=0.7)
            plt.title(f'{ticker} MACD Indicator')
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.read()).decode('utf-8')
            plt.close()
            logger.debug(f"Successfully plotted MACD for {ticker}.")
            return img_str
        except KeyError as e:
            logger.error(f"Error plotting MACD: Missing column {e}. Ensure 'Date', 'MACD', 'Signal_Line', and 'Histogram' columns exist.", exc_info=True)
            return f"Error: Missing data for plotting MACD: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during plotting MACD for {ticker}: {e}", exc_info=True)
            return f"Error: An unexpected error occurred during plotting MACD for {ticker}: {e}"

    def plot_rsi(self, data: pd.DataFrame, ticker: str) -> str:
        """
        Generates a plot of RSI.

        Args:
            data: DataFrame with 'Date' and 'RSI' columns.
            ticker: Stock ticker symbol.

        Returns:
            A base64 encoded string of the plot image.
        """
        logger.debug(f"Attempting to plot RSI for {ticker}.")
        try:
            df = self._to_dataframe(data)
            if df.empty or "Date" not in df.columns:
                return "Error: Missing data for plotting RSI. Ensure 'Date' and 'Close' are available."

            if "RSI" in df.columns:
                plot_df = df
            else:
                if "Close" not in df.columns:
                    return "Error: Missing 'Close' data for RSI calculation."
                plot_df = df.copy()
                plot_df["RSI"] = talib.RSI(plot_df["Close"])
                logger.debug("Computed RSI from Close prices for plotting.")

            plot_df = plot_df.dropna(subset=["RSI"])
            if plot_df.empty:
                return "Error: Not enough data points to plot RSI."

            plt.figure(figsize=(10, 6))
            plt.plot(plot_df['Date'], plot_df['RSI'], label='RSI', color='purple')
            plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
            plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')
            plt.title(f'{ticker} RSI Indicator')
            plt.xlabel('Date')
            plt.ylabel('RSI Value')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.read()).decode('utf-8')
            plt.close()
            logger.debug(f"Successfully plotted RSI for {ticker}.")
            return img_str
        except KeyError as e:
            logger.error(f"Error plotting RSI: Missing column {e}. Ensure 'Date' and 'RSI' columns exist.", exc_info=True)
            return f"Error: Missing data for plotting RSI: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during plotting RSI for {ticker}: {e}", exc_info=True)
            return f"Error: An unexpected error occurred during plotting RSI for {ticker}: {e}"
