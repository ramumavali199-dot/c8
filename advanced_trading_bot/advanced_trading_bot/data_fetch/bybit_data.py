import time
import requests

BASE_URL = "https://api.bybit.com"

def _kline(category: str, symbol: str, interval: str, limit: int = 300):
    """
    Fetch klines from Bybit v5.
    category: "linear" (USDT Perp), "inverse", or "spot"
    interval: "1", "3", "5", "15", "30", "60", "120", "240", "D", etc.
    """
    # Map our friendly TFs to Bybit intervals
    tf_map = {
        "1m": "1", "3m": "3", "5m": "5", "15m": "15", "30m": "30",
        "1h": "60", "2h": "120", "4h": "240", "1d": "D"
    }
    bybit_interval = tf_map.get(interval, interval)
    url = f"{BASE_URL}/v5/market/kline"
    params = {
        "category": category,
        "symbol": symbol,
        "interval": bybit_interval,
        "limit": min(limit, 1000)
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("retCode") != 0:
        raise RuntimeError(f"Bybit error: {data}")
    # data['result']['list'] => list of [startTime, open, high, low, close, volume, turnover]
    return data["result"]["list"]

def get_klines(symbol: str, interval: str, limit: int = 300):
    """
    Try linear futures first, then fallback to spot.
    Returns list of candles sorted by time ascending.
    """
    for category in ("linear", "spot"):
        try:
            rows = _kline(category, symbol, interval, limit)
            # Ensure ascending order
            rows = sorted(rows, key=lambda x: int(x[0]))
            return rows
        except Exception as e:
            last_err = e
    raise last_err
