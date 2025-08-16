from typing import Dict, Any, List, Tuple
import math

import pandas as pd
import numpy as np

# ------------------
# Indicator helpers
# ------------------
def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()

def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(length).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    fast_ema = ema(series, fast)
    slow_ema = ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def bollinger(series: pd.Series, length: int = 20, mult: float = 2.0):
    basis = series.rolling(length).mean()
    dev = series.rolling(length).std(ddof=0)
    upper = basis + mult * dev
    lower = basis - mult * dev
    return basis, upper, lower

def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr

def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    tr = true_range(high, low, close)
    return tr.rolling(length).mean()

# ------------------
# Signal logic
# ------------------
def compute_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """
    df columns expected: ['ts','open','high','low','close','volume']
    Returns a dict with direction, confidence, atr, details.
    """
    if df is None or df.empty or len(df) < 50:
        return {"signal": None, "reason": "not-enough-data"}

    df = df.copy()
    df["ema9"] = ema(df["close"], 9)
    df["ema21"] = ema(df["close"], 21)
    df["rsi"] = rsi(df["close"], 14)
    macd_line, signal_line, hist = macd(df["close"])
    df["macd_line"] = macd_line
    df["macd_signal"] = signal_line
    basis, upper, lower = bollinger(df["close"], 20, 2.0)
    df["bb_basis"], df["bb_upper"], df["bb_lower"] = basis, upper, lower
    df["atr14"] = atr(df["high"], df["low"], df["close"], 14)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Filters (5 total)
    ema_cross_buy = last["ema9"] > last["ema21"]
    ema_cross_sell = last["ema9"] < last["ema21"]

    rsi_buy = last["rsi"] > 55
    rsi_sell = last["rsi"] < 45

    macd_buy = last["macd_line"] > last["macd_signal"]
    macd_sell = last["macd_line"] < last["macd_signal"]

    # Bollinger: near lower => potential rebound (buy), near upper => potential rejection (sell)
    # We'll define "near" as within 10% of band distance.
    bb_range = max(1e-6, last["bb_upper"] - last["bb_lower"])
    near_lower = (last["close"] - last["bb_lower"]) / bb_range <= 0.10
    near_upper = (last["bb_upper"] - last["close"]) / bb_range <= 0.10
    bb_buy = near_lower
    bb_sell = near_upper

    # Volume spike: latest volume > 1.5 * average of last 20
    vol_spike = last["volume"] > 1.5 * df["volume"].tail(21).iloc[:-1].mean()
    vol_buy = vol_spike
    vol_sell = vol_spike

    buy_score = sum([ema_cross_buy, rsi_buy, macd_buy, bb_buy, vol_buy])
    sell_score = sum([ema_cross_sell, rsi_sell, macd_sell, bb_sell, vol_sell])

    direction = None
    score = 0
    if buy_score > sell_score and buy_score >= 3:
        direction = "BUY"
        score = buy_score
    elif sell_score > buy_score and sell_score >= 3:
        direction = "SELL"
        score = sell_score

    if direction is None:
        return {"signal": None, "reason": "no-confirmation"}

    confidence = (score / 5) * 100.0

    return {
        "signal": direction,
        "confidence": confidence,
        "close": float(last["close"]),
        "atr": float(last["atr14"]),
        "details": {
            "ema9": float(last["ema9"]), "ema21": float(last["ema21"]),
            "rsi": float(last["rsi"]),
            "macd_line": float(last["macd_line"]), "macd_signal": float(last["macd_signal"]),
            "bb_upper": float(last["bb_upper"]), "bb_lower": float(last["bb_lower"]),
            "volume": float(last["volume"])
        }
    }

def assemble_df_from_klines(rows: List[List]) -> pd.DataFrame:
    """
    Convert Bybit-style klines to DataFrame with ['ts','open','high','low','close','volume']
    rows: list of [startTime, open, high, low, close, volume, turnover]
    Or generic: [ts, o, h, l, c, v]
    """
    if not rows:
        return pd.DataFrame()
    # Normalize numbers
    norm = []
    for r in rows:
        # If string values, cast
        if isinstance(r[1], str):
            o, h, l, c, v = map(float, r[1:6])
            ts = int(r[0])
        else:
            ts, o, h, l, c, v = int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])
        norm.append([ts, o, h, l, c, v])
    df = pd.DataFrame(norm, columns=["ts","open","high","low","close","volume"])
    return df
