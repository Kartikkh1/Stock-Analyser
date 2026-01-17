import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

class VisualizationTools:
    @staticmethod
    def plot_stock_prices(historical_data: pd.DataFrame, ticker: str) -> str:
        """
        Generates a line plot of historical stock prices.

        Args:
            historical_data: DataFrame with 'Date' and 'Close' columns.
            ticker: Stock ticker symbol.

        Returns:
            A base64 encoded string of the plot image.
        """
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(historical_data['Date'], historical_data['Close'], marker='o', linestyle='-')
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
            return img_str
        except KeyError as e:
            print(f"Error plotting stock prices: Missing column {e}. Ensure 'Date' and 'Close' columns exist.")
            return f"Error: Missing data for plotting stock prices: {e}"
        except Exception as e:
            print(f"An unexpected error occurred during plotting stock prices for {ticker}: {e}")
            return f"Error: An unexpected error occurred during plotting stock prices for {ticker}: {e} கவனம்"

    @staticmethod
    def plot_macd(data: pd.DataFrame, ticker: str) -> str:
        """
        Generates a plot of MACD and Signal Line.

        Args:
            data: DataFrame with 'Date', 'MACD', and 'Signal_Line' columns.
            ticker: Stock ticker symbol.

        Returns:
            A base64 encoded string of the plot image.
        """
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(data['Date'], data['MACD'], label='MACD', color='blue')
            plt.plot(data['Date'], data['Signal_Line'], label='Signal Line', color='red')
            plt.bar(data['Date'], data['Histogram'], label='Histogram', color='gray', alpha=0.7)
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
            return img_str
        except KeyError as e:
            print(f"Error plotting MACD: Missing column {e}. Ensure 'Date', 'MACD', 'Signal_Line', and 'Histogram' columns exist.")
            return f"Error: Missing data for plotting MACD: {e}"
        except Exception as e:
            print(f"An unexpected error occurred during plotting MACD for {ticker}: {e}")
            return f"Error: An unexpected error occurred during plotting MACD for {ticker}: {e}"

    @staticmethod
    def plot_rsi(data: pd.DataFrame, ticker: str) -> str:
        """
        Generates a plot of RSI.

        Args:
            data: DataFrame with 'Date' and 'RSI' columns.
            ticker: Stock ticker symbol.

        Returns:
            A base64 encoded string of the plot image.
        """
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(data['Date'], data['RSI'], label='RSI', color='purple')
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
            return img_str
        except KeyError as e:
            print(f"Error plotting RSI: Missing column {e}. Ensure 'Date' and 'RSI' columns exist.")
            return f"Error: Missing data for plotting RSI: {e}"
        except Exception as e:
            print(f"An unexpected error occurred during plotting RSI for {ticker}: {e}")
            return f"Error: An unexpected error occurred during plotting RSI for {ticker}: {e}"
