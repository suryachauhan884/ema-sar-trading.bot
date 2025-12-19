# ======================================================
# EMA + PARABOLIC SAR PRO TRADING BOT
# FINAL ALL-IN-ONE | RAILWAY | TERMUX
# ======================================================

import os
import requests
import sqlite3
import threading
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from fastapi import FastAPI
import uvicorn

# ======================================================
# CONFIG (USE RAILWAY VARIABLES)
# ======================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PORT = int(os.getenv("PORT", 8000))

SYMBOL = "BTCUSDT"        # change later if needed
PAIR_NAME = "BTC/USDT"

# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(level=logging.INFO)

# ======================================================
# DATABASE (WIN / LOSS STORAGE)
# ======================================================

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair TEXT,
    signal TEXT,
    confidence REAL,
    time TEXT
)
""")
conn.commit()

# ======================================================
# BINANCE DATA + INDICATORS
# ======================================================

def fetch_klines(symbol, limit=100):
    url = (
        "https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval=1m&limit={limit}"
    )
    data = requests.get(url, timeout=10).json()
    closes = [float(c[4]) for c in data]
    highs = [float(c[2]) for c in data]
    lows = [float(c[3]) for c in data]
    return closes, highs, lows


def ema(prices, period):
    k = 2 / (period + 1)
    value = prices[0]
    for p in prices[1:]:
        value = p * k + value * (1 - k)
    return value


def parabolic_sar(highs, lows, af=0.02, max_af=0.2):
    sar = lows[0]
    ep = highs[0]
    accel = af
    uptrend = True

    for i in range(1, len(highs)):
        sar = sar + accel * (ep - sar)

        if uptrend:
            if lows[i] < sar:
                uptrend = False
                sar = ep
                ep = lows[i]
                accel = af
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    accel = min(accel + af, max_af)
        else:
            if highs[i] > sar:
                uptrend = True
                sar = ep
                ep = highs[i]
                accel = af
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    accel = min(accel + af, max_af)

    return sar


def get_ema_sar_signal():
    closes, highs, lows = fetch_klines(SYMBOL)

    ema9 = ema(closes[-30:], 9)
    ema21 = ema(closes[-30:], 21)
    sar = parabolic_sar(highs[-30:], lows[-30:])
    price = closes[-1]

    if ema9 > ema21 and price > sar:
        signal = "BUY"
    elif ema9 < ema21 and price < sar:
        signal = "SELL"
    else:
        signal = "WAIT"

    confidence = round(
        min(95, abs(ema9 - ema21) * 100 + abs(price - sar)),
        2
    )

    return signal, confidence, price

# ======================================================
# TELEGRAM DASHBOARD
# ======================================================

def dashboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Live Signal", callback_data="signal")],
        [InlineKeyboardButton("📈 Stats", callback_data="stats")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *EMA SAR PRO BOT*\n\n"
        "Live EMA(9/21) + Parabolic SAR\n"
        "Binance 1-minute candles\n\n"
        "Choose an option:",
        parse_mode="Markdown",
        reply_markup=dashboard()
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "signal":
        signal, confidence, price = get_ema_sar_signal()

        cur.execute(
            "INSERT INTO signals (pair, signal, confidence, time) VALUES (?,?,?,?)",
            (PAIR_NAME, signal, confidence, datetime.now().isoformat())
        )
        conn.commit()

        msg = (
            f"📊 *LIVE SIGNAL*\n\n"
            f"Pair: *{PAIR_NAME}*\n"
            f"Price: `{price}`\n"
            f"Signal: *{signal}*\n"
            f"Confidence: *{confidence}%*"
        )

        await q.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=dashboard()
        )

    elif q.data == "stats":
        cur.execute("SELECT COUNT(*) FROM signals WHERE signal='BUY'")
        buys = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM signals WHERE signal='SELL'")
        sells = cur.fetchone()[0]

        await q.edit_message_text(
            f"📈 *Signal Stats*\n\n"
            f"BUY: {buys}\n"
            f"SELL: {sells}",
            parse_mode="Markdown",
            reply_markup=dashboard()
        )

# ======================================================
# FASTAPI (RAILWAY HEALTH)
# ======================================================

api = FastAPI()

@api.get("/")
def root():
    return {"status": "EMA SAR BOT RUNNING"}

def run_api():
    uvicorn.run(api, host="0.0.0.0", port=PORT)

# ======================================================
# MAIN
# ======================================================

def main():
    print("🤖 EMA SAR BOT RUNNING (REAL EMA + SAR)")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))

    threading.Thread(target=run_api, daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
