# =================================================
# Aggressive EMA + SAR Signal Logic
# =================================================

def aggressive_signal(close, ema_fast, ema_slow, sar):
    """
    Aggressive EMA + SAR strategy
    """

    # BUY condition
    if close > ema_fast > ema_slow and sar < close:
        return "BUY"

    # SELL condition
    if close < ema_fast < ema_slow and sar > close:
        return "SELL"

    return "WAIT"
