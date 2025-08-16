import os

# --------------------
# General Settings
# --------------------
TIMEFRAMES = ["5m", "15m", "1h", "4h", "1d"]
ALERT_MODE = os.getenv("ALERT_MODE", "short")  # "short" or "detailed"
CONFIDENCE_DECIMALS = int(os.getenv("CONFIDENCE_DECIMALS", "0"))  # 0 => 82% ; 1 => 82.5%

# --------------------
# Crypto (Bybit)
# --------------------
CRYPTO_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "DOGEUSDT", "ADAUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT"
]

# --------------------
# Indian Stocks (NSE)
# --------------------
STOCK_SYMBOLS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "KOTAKBANK", "SBIN", "HINDUNILVR", "LT", "BAJFINANCE"
]

# --------------------
# Indian Indices
# --------------------
INDEX_SYMBOLS = [
    "NIFTY",        # NIFTY 50
    "BANKNIFTY",    # Bank Nifty
    "SENSEX",       # BSE Sensex
    "MIDCPNIFTY"    # Nifty Midcap Select
]

# --------------------
# Telegram Alerts
# --------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ENABLE_ALERTS = os.getenv("ENABLE_ALERTS", "true").lower() == "true"

# --------------------
# Upstox / NSE data access (optional)
# --------------------
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY", "")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET", "")
UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN", "")  # OAuth token if you have it

# How many candles to pull per symbol per TF
CANDLES_LIMIT = int(os.getenv("CANDLES_LIMIT", "300"))
