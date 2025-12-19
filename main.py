from fastapi import FastAPI
import requests
from datetime import datetime
from indicators import ema, rsi, parabolic_sar

app = FastAPI()

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def get_prices(symbol="BTCUSDT", interval="1m", limit=50):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    data = requests.get(BINANCE_URL, params=params).json()
    closes = [float(candle[4]) for candle in data]
    highs = [float(candle[2]) for candle in data]
    lows = [float(candle[3]) for candle in data]
    return closes, highs, lows


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/signal")
def signal(symbol: str = "BTCUSDT"):
    closes, highs, lows = get_prices(symbol)

    ema_fast = ema(closes[-20:], 9)
    ema_slow = ema(closes[-20:], 21)
    rsi_val = rsi(closes)
    sar_ok = parabolic_sar(highs, lows)

    action = "WAIT"
    confidence = 0

    if ema_fast > ema_slow and rsi_val < 70 and sar_ok:
        action = "BUY"
        confidence = 85

    elif ema_fast < ema_slow and rsi_val > 30 and not sar_ok:
        action = "SELL"
        confidence = 85

    return {
        "asset": symbol,
        "action": action,
        "ema_fast": round(ema_fast, 4),
        "ema_slow": round(ema_slow, 4),
        "rsi": round(rsi_val, 2),
        "confidence": confidence,
        "timeframe": "1 MIN",
        "time": datetime.utcnow()
    }
