from typing import Any

import pandas as pd
import talib
from crewai.tools import tool

from stock_analyser.utils.logger import logger


def _to_dataframe(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif isinstance(data, dict):
        if "candles" in data:
            df = pd.DataFrame(data.get("candles", []))
        else:
            df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data)

    if df.empty:
        return df

    rename_map: dict[str, str] = {}
    for col in df.columns:
        lower = str(col).lower()
        if lower == "close":
            rename_map[col] = "close"
        elif lower == "high":
            rename_map[col] = "high"
        elif lower == "low":
            rename_map[col] = "low"
        elif lower == "open":
            rename_map[col] = "open"
        elif lower == "date":
            rename_map[col] = "date"
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


@tool("calculate_ichimoku_cloud")
def calculate_ichimoku_cloud(df: Any) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Calculates the Ichimoku Cloud for a given DataFrame of historical prices.
    The data should have 'high', 'low', 'close' columns.
    """
    logger.debug("Calculating Ichimoku Cloud.")
    try:
        data = _to_dataframe(df)
        if data.empty:
            return {"error": "Missing data for Ichimoku Cloud calculation: empty dataset"}
        if not {"high", "low", "close"}.issubset(data.columns):
            return {"error": "Missing data for Ichimoku Cloud calculation: requires high, low, close"}

        high_9 = data["high"].rolling(window=9).max()
        low_9 = data["low"].rolling(window=9).min()
        data["tenkan_sen"] = (high_9 + low_9) / 2

        high_26 = data["high"].rolling(window=26).max()
        low_26 = data["low"].rolling(window=26).min()
        data["kijun_sen"] = (high_26 + low_26) / 2

        data["senkou_span_a"] = ((data["tenkan_sen"] + data["kijun_sen"]) / 2).shift(26)

        high_52 = data["high"].rolling(window=52).max()
        low_52 = data["low"].rolling(window=52).min()
        data["senkou_span_b"] = ((high_52 + low_52) / 2).shift(26)

        data["chikou_span"] = data["close"].shift(-26)

        logger.debug("Ichimoku Cloud calculated successfully.")
        return data[["tenkan_sen", "kijun_sen", "senkou_span_a", "senkou_span_b", "chikou_span"]].to_dict("records")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ichimoku Cloud calculation: {e}", exc_info=True)
        return {"error": str(e)}


@tool("calculate_fibonacci_retracements")
def calculate_fibonacci_retracements(high: float, low: float) -> dict[str, Any]:
    """
    Calculates Fibonacci Retracement levels given a high and a low point.
    """
    logger.debug(f"Calculating Fibonacci Retracements for high: {high}, low: {low}")
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
        logger.debug("Fibonacci Retracements calculated successfully.")
        return levels
    except Exception as e:
        logger.error(f"An unexpected error occurred during Fibonacci Retracements calculation: {e}", exc_info=True)
        return {"error": str(e)}


@tool("calculate_moving_averages")
def calculate_moving_averages(df: Any, timeperiod: int = 20) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Calculates Simple Moving Average (SMA) and Exponential Moving Average (EMA).
    The data should have a 'close' column.
    """
    logger.debug(f"Calculating Moving Averages with timeperiod: {timeperiod}")
    try:
        data = _to_dataframe(df)
        if data.empty:
            return {"error": "Missing data for Moving Averages calculation: empty dataset"}
        if "close" not in data.columns:
            return {"error": "Missing data for Moving Averages calculation: requires close"}

        data["SMA"] = talib.SMA(data["close"], timeperiod=timeperiod)
        data["EMA"] = talib.EMA(data["close"], timeperiod=timeperiod)
        logger.debug("Moving Averages calculated successfully.")
        return data[["SMA", "EMA"]].to_dict("records")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Moving Averages calculation: {e}", exc_info=True)
        return {"error": str(e)}


@tool("calculate_rsi")
def calculate_rsi(df: Any, timeperiod: int = 14) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Calculates the Relative Strength Index (RSI).
    The data should have a 'close' column.
    """
    logger.debug(f"Calculating RSI with timeperiod: {timeperiod}")
    try:
        data = _to_dataframe(df)
        if data.empty:
            return {"error": "Missing data for RSI calculation: empty dataset"}
        if "close" not in data.columns:
            return {"error": "Missing data for RSI calculation: requires close"}

        data["RSI"] = talib.RSI(data["close"], timeperiod=timeperiod)
        logger.debug("RSI calculated successfully.")
        return data[["RSI"]].to_dict("records")
    except Exception as e:
        logger.error(f"An unexpected error occurred during RSI calculation: {e}", exc_info=True)
        return {"error": str(e)}


@tool("calculate_macd")
def calculate_macd(
    df: Any, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9
) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Calculates the Moving Average Convergence Divergence (MACD).
    The data should have a 'close' column.
    """
    logger.debug(
        f"Calculating MACD with fastperiod: {fastperiod}, slowperiod: {slowperiod}, signalperiod: {signalperiod}"
    )
    try:
        data = _to_dataframe(df)
        if data.empty:
            return {"error": "Missing data for MACD calculation: empty dataset"}
        if "close" not in data.columns:
            return {"error": "Missing data for MACD calculation: requires close"}

        macd, macdsignal, macdhist = talib.MACD(
            data["close"], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod
        )
        data["MACD"] = macd
        data["MACD_Signal"] = macdsignal
        data["MACD_Hist"] = macdhist
        logger.debug("MACD calculated successfully.")
        return data[["MACD", "MACD_Signal", "MACD_Hist"]].to_dict("records")
    except Exception as e:
        logger.error(f"An unexpected error occurred during MACD calculation: {e}", exc_info=True)
        return {"error": str(e)}


@tool("calculate_bollinger_bands")
def calculate_bollinger_bands(
    df: Any, timeperiod: int = 20, nbdevup: int = 2, nbdevdn: int = 2
) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Calculates Bollinger Bands.
    The data should have a 'close' column.
    """
    logger.debug(f"Calculating Bollinger Bands with timeperiod: {timeperiod}")
    try:
        data = _to_dataframe(df)
        if data.empty:
            return {"error": "Missing data for Bollinger Bands calculation: empty dataset"}
        if "close" not in data.columns:
            return {"error": "Missing data for Bollinger Bands calculation: requires close"}

        upper, middle, lower = talib.BBANDS(
            data["close"], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn
        )
        data["Bollinger_Upper"] = upper
        data["Bollinger_Middle"] = middle
        data["Bollinger_Lower"] = lower
        logger.debug("Bollinger Bands calculated successfully.")
        return data[["Bollinger_Upper", "Bollinger_Middle", "Bollinger_Lower"]].to_dict("records")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Bollinger Bands calculation: {e}", exc_info=True)
        return {"error": str(e)}


@tool("calculate_atr")
def calculate_atr(df: Any, timeperiod: int = 14) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Calculates the Average True Range (ATR).
    The data should have 'high', 'low', 'close' columns.
    """
    logger.debug(f"Calculating ATR with timeperiod: {timeperiod}")
    try:
        data = _to_dataframe(df)
        if data.empty:
            return {"error": "Missing data for ATR calculation: empty dataset"}
        if not {"high", "low", "close"}.issubset(data.columns):
            return {"error": "Missing data for ATR calculation: requires high, low, close"}

        data["ATR"] = talib.ATR(data["high"], data["low"], data["close"], timeperiod=timeperiod)
        logger.debug("ATR calculated successfully.")
        return data[["ATR"]].to_dict("records")
    except Exception as e:
        logger.error(f"An unexpected error occurred during ATR calculation: {e}", exc_info=True)
        return {"error": str(e)}


def get_technical_analysis_tools() -> list[Any]:
    return [
        calculate_ichimoku_cloud,
        calculate_fibonacci_retracements,
        calculate_moving_averages,
        calculate_rsi,
        calculate_macd,
        calculate_bollinger_bands,
        calculate_atr,
    ]
