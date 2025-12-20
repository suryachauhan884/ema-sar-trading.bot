from fastapi import FastAPI
from indicators import aggressive_signal

app = FastAPI(title="TradeWin API")

# =================================================
# Binary (Olymp Trade) Signal API
# =================================================

@app.get("/api/binary/signal")
def binary_signal():
    """
    Live-style aggressive EMA + SAR signal
    (Safe model – no scraping)
    """

    # --- Simulated LIVE candle values ---
    close = 1.1708
    ema_fast = 1.1706
    ema_slow = 1.1703
    sar = 1.1701

    signal = aggressive_signal(
        close=close,
        ema_fast=ema_fast,
        ema_slow=ema_slow,
        sar=sar
    )

    confidence = 85 if signal != "WAIT" else 40

    return {
        "broker": "Olymp Trade",
        "pair": "EUR/USD",
        "timeframe": "1 Min",
        "signal": signal,
        "confidence": confidence,
        "strategy": "Aggressive EMA + SAR",
        "status": "LIVE"
    }


# =================================================
# Health Check (IMPORTANT for Railway)
# =================================================

@app.get("/")
def root():
    return {"status": "TradeWin API Running"}
