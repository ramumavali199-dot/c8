"""
Lightweight placeholder fetcher for Indian stocks/indices.
- If UPSTOX_ACCESS_TOKEN is set, you can integrate real Upstox APIs here.
- Otherwise, this module raises NotImplementedError, so main will skip stocks/indices scan.
"""
from typing import List

def get_klines(symbol: str, interval: str, limit: int = 300):
    """
    Replace with actual Upstox / NSE data provider.
    Expected return format: list of candles [[ts, open, high, low, close, volume], ...] ascending ts.
    """
    raise NotImplementedError("Upstox/NSE data fetch not configured. Provide an implementation or access token.")
