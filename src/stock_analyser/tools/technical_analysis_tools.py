import pandas as pd
from crewai_tools import BaseTool
import talib

class TechnicalAnalysisTools(BaseTool):
    name: str = "Technical Analysis Tools"
    description: str = "A collection of tools for calculating various technical indicators."

    def _run(self, tool_name: str, **kwargs):
        if tool_name == "calculate_ichimoku_cloud":
            return self._calculate_ichimoku_cloud(**kwargs)
        elif tool_name == "calculate_fibonacci_retracements":
            return self._calculate_fibonacci_retracements(**kwargs)
        elif tool_name == "calculate_moving_averages":
            return self._calculate_moving_averages(**kwargs)
        elif tool_name == "calculate_rsi":
            return self._calculate_rsi(**kwargs)
        elif tool_name == "calculate_macd":
            return self._calculate_macd(**kwargs)
        elif tool_name == "calculate_bollinger_bands":
            return self._calculate_bollinger_bands(**kwargs)
        elif tool_name == "calculate_atr":
            return self._calculate_atr(**kwargs)
        else:
            raise ValueError(f"Unknown tool name: {tool_name}")

    def _calculate_ichimoku_cloud(self, df: pd.DataFrame):
        """
        Calculates the Ichimoku Cloud for a given DataFrame of historical prices.
        The DataFrame should have 'high', 'low', 'close' columns.
        """
        try:
            # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
            high_9 = df['high'].rolling(window=9).max()
            low_9 = df['low'].rolling(window=9).min()
            df['tenkan_sen'] = (high_9 + low_9) / 2

            # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
            high_26 = df['high'].rolling(window=26).max()
            low_26 = df['low'].rolling(window=26).min()
            df['kijun_sen'] = (high_26 + low_26) / 2

            # Senkou Span A (Leading Span A): (Conversion Line + Base Line) / 2 plotted 26 periods ahead
            df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

            # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2 plotted 26 periods ahead
            high_52 = df['high'].rolling(window=52).max()
            low_52 = df['low'].rolling(window=52).min()
            df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

            # Chikou Span (Lagging Span): Close plotted 26 periods behind
            df['chikou_span'] = df['close'].shift(-26)

            return df[['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span']].to_dict('records')
        except KeyError as e:
            print(f"Error in Ichimoku Cloud calculation: Missing column {e}. Ensure 'high', 'low', 'close' columns exist.")
            return {"error": f"Missing data for Ichimoku Cloud calculation: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during Ichimoku Cloud calculation: {e}")
            return {"error": str(e)}

    def _calculate_fibonacci_retracements(self, high: float, low: float):
        """
        Calculates Fibonacci Retracement levels given a high and a low point.
        """
        try:
            diff = high - low
            levels = {
                "0%": high,
                "23.6%": high - 0.236 * diff,
                "38.2%": high - 0.382 * diff,
                "50%": high - 0.5 * diff,
                "61.8%": high - 0.618 * diff,
                "100%": low,
            }
            return levels
        except Exception as e:
            print(f"An unexpected error occurred during Fibonacci Retracements calculation: {e}")
            return {"error": str(e)}

    def _calculate_moving_averages(self, df: pd.DataFrame, timeperiod: int = 20):
        """
        Calculates Simple Moving Average (SMA) and Exponential Moving Average (EMA).
        The DataFrame should have a 'close' column.
        """
        try:
            df['SMA'] = talib.SMA(df['close'], timeperiod=timeperiod)
            df['EMA'] = talib.EMA(df['close'], timeperiod=timeperiod)
            return df[['SMA', 'EMA']].to_dict('records')
        except KeyError as e:
            print(f"Error in Moving Averages calculation: Missing column {e}. Ensure 'close' column exists.")
            return {"error": f"Missing data for Moving Averages calculation: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during Moving Averages calculation: {e}")
            return {"error": str(e)}

    def _calculate_rsi(self, df: pd.DataFrame, timeperiod: int = 14):
        """
        Calculates the Relative Strength Index (RSI).
        The DataFrame should have a 'close' column.
        """
        try:
            df['RSI'] = talib.RSI(df['close'], timeperiod=timeperiod)
            return df[['RSI']].to_dict('records')
        except KeyError as e:
            print(f"Error in RSI calculation: Missing column {e}. Ensure 'close' column exists.")
            return {"error": f"Missing data for RSI calculation: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during RSI calculation: {e}")
            return {"error": str(e)}

    def _calculate_macd(self, df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9):
        """
        Calculates the Moving Average Convergence Divergence (MACD).
        The DataFrame should have a 'close' column.
        """
        try:
            macd, macdsignal, macdhist = talib.MACD(df['close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
            df['MACD'] = macd
            df['MACD_Signal'] = macdsignal
            df['MACD_Hist'] = macdhist
            return df[['MACD', 'MACD_Signal', 'MACD_Hist']].to_dict('records')
        except KeyError as e:
            print(f"Error in MACD calculation: Missing column {e}. Ensure 'close' column exists.")
            return {"error": f"Missing data for MACD calculation: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during MACD calculation: {e}")
            return {"error": str(e)}

    def _calculate_bollinger_bands(self, df: pd.DataFrame, timeperiod: int = 20, nbdevup: int = 2, nbdevdn: int = 2):
        """
        Calculates Bollinger Bands.
        The DataFrame should have a 'close' column.
        """
        try:
            upper, middle, lower = talib.BBANDS(df['close'], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
            df['Bollinger_Upper'] = upper
            df['Bollinger_Middle'] = middle
            df['Bollinger_Lower'] = lower
            return df[['Bollinger_Upper', 'Bollinger_Middle', 'Bollinger_Lower']].to_dict('records')
        except KeyError as e:
            print(f"Error in Bollinger Bands calculation: Missing column {e}. Ensure 'close' column exists.")
            return {"error": f"Missing data for Bollinger Bands calculation: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during Bollinger Bands calculation: {e}")
            return {"error": str(e)}

    def _calculate_atr(self, df: pd.DataFrame, timeperiod: int = 14):
        """
        Calculates the Average True Range (ATR).
        The DataFrame should have 'high', 'low', 'close' columns.
        """
        try:
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=timeperiod)
            return df[['ATR']].to_dict('records')
        except KeyError as e:
            print(f"Error in ATR calculation: Missing column {e}. Ensure 'high', 'low', 'close' columns exist.")
            return {"error": f"Missing data for ATR calculation: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during ATR calculation: {e}")
            return {"error": str(e)}
