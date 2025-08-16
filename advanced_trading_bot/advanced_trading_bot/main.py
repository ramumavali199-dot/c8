import os
import time
from typing import List

from config.config import (
    TIMEFRAMES, CRYPTO_SYMBOLS, STOCK_SYMBOLS, INDEX_SYMBOLS,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ENABLE_ALERTS,
    CANDLES_LIMIT, CONFIDENCE_DECIMALS
)
from alerts.telegram_bot import send_telegram_message
from data_fetch.bybit_data import get_klines as bybit_klines
from data_fetch.upstox_data import get_klines as upstox_klines
from strategies.multi_tf_scanner import compute_signals, assemble_df_from_klines
from utils.targets import calc_tp_sl_from_atr
from ml.model import boost_confidence

def fmt_confidence(conf: float) -> str:
    if CONFIDENCE_DECIMALS <= 0:
        return f"{round(conf):.0f}%"
    return f"{conf:.{CONFIDENCE_DECIMALS}f}%"

def make_alert_line(asset_type: str, symbol: str, direction: str, price: float, tp: float, sl: float, conf: float) -> str:
    # SHORT format requested by user:
    # [ASSET] SYMBOL BUY @ 2930 | TP: 2950 | SL: 2910 | Confidence: 82%
    return f"[{asset_type}] {symbol} {direction} @ {round(price, 2)} | TP: {tp} | SL: {sl} | Confidence: {fmt_confidence(conf)}"

def scan_crypto():
    alerts = []
    for tf in TIMEFRAMES:
        for sym in CRYPTO_SYMBOLS:
            try:
                rows = bybit_klines(sym, tf, CANDLES_LIMIT)
                df = assemble_df_from_klines(rows)
                res = compute_signals(df)
                if res.get("signal"):
                    direction = res["signal"]
                    conf = boost_confidence(res["confidence"])
                    tp, sl = calc_tp_sl_from_atr(res["close"], res["atr"], direction)
                    line = make_alert_line("CRYPTO", sym, direction, res["close"], tp, sl, conf)
                    alerts.append(line)
            except Exception as e:
                print(f"[crypto] {sym} {tf} error:", e)
    return alerts

def scan_upstox(symbols: List[str], label: str):
    alerts = []
    for tf in TIMEFRAMES:
        for sym in symbols:
            try:
                rows = upstox_klines(sym, tf, CANDLES_LIMIT)
                df = assemble_df_from_klines(rows)
                res = compute_signals(df)
                if res.get("signal"):
                    direction = res["signal"]
                    conf = boost_confidence(res["confidence"])
                    tp, sl = calc_tp_sl_from_atr(res["close"], res["atr"], direction)
                    line = make_alert_line(label, sym, direction, res["close"], tp, sl, conf)
                    alerts.append(line)
            except NotImplementedError as e:
                print(f"[{label.lower()}] Upstox/NSE not configured for {sym}. Skipping. ({e})")
                return alerts
            except Exception as e:
                print(f"[{label.lower()}] {sym} {tf} error:", e)
    return alerts

def main():
    print("=== Advanced Trading Bot (Multi-confirmation) ===")
    crypto_alerts = scan_crypto()
    stock_alerts = scan_upstox(STOCK_SYMBOLS, "STOCK")
    index_alerts = scan_upstox(INDEX_SYMBOLS, "INDEX")

    all_alerts = crypto_alerts + stock_alerts + index_alerts

    if not all_alerts:
        print("No signals at this run.")
        return

    for msg in all_alerts:
        print("ALERT:", msg)
        if ENABLE_ALERTS:
            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)
        time.sleep(0.4)  # avoid flooding

if __name__ == "__main__":
    main()
