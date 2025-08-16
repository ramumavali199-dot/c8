def calc_tp_sl_from_atr(close: float, atr: float, direction: str):
    """
    TP = ATR * 1.8
    SL = ATR * 1.0
    For BUY: TP above, SL below. For SELL: TP below, SL above.
    """
    tp_off = atr * 1.8
    sl_off = atr * 1.0
    if direction.upper() == "BUY":
        tp = close + tp_off
        sl = close - sl_off
    else:
        tp = close - tp_off
        sl = close + sl_off
    return round(tp, 2), round(sl, 2)
