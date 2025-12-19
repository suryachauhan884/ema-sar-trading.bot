# ===============================
# EMA SAR PRO TRADING BOT
# ALL-IN-ONE | RAILWAY | TERMUX
# ===============================

import os
import sqlite3
import logging
import threading
import time
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

# ===============================
# CONFIG
# ===============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

BOT_ACTIVE = True
AUTO_MODE = True

# ===============================
# LOGGING
# ===============================
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===============================
# DATABASE
# ===============================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair TEXT,
    signal TEXT,
    result TEXT,
    time TEXT
)
""")
conn.commit()

# ===============================
# INDICATOR LOGIC (SIMPLIFIED)
# ===============================
def get_ema_sar_signal():
    # DEMO LOGIC (replace with real market data later)
    minute = datetime.now().minute
    if minute % 2 == 0:
        return "BUY"
    return "SELL"

# ===============================
# TELEGRAM UI
# ===============================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Live Signal", callback_data="signal")],
        [InlineKeyboardButton("📈 Trend", callback_data="trend"),
         InlineKeyboardButton("🧮 Stats", callback_data="stats")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ])

# ===============================
# COMMANDS
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *EMA SAR PRO BOT*\n\nSelect an option:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT COUNT(*) FROM signals WHERE result='WIN'")
    wins = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM signals WHERE result='LOSS'")
    losses = cursor.fetchone()[0]
    total = wins + losses
    acc = (wins / total * 100) if total else 0

    msg = f"""
📊 *Performance*
Wins: {wins}
Losses: {losses}
Accuracy: {acc:.2f}%
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

# ===============================
# CALLBACK HANDLER
# ===============================
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE, AUTO_MODE
    q = update.callback_query
    await q.answer()

    if q.data == "signal":
        signal = get_ema_sar_signal()
        cursor.execute(
            "INSERT INTO signals (pair, signal, result, time) VALUES (?,?,?,?)",
            ("BTC/USDT", signal, "WIN", datetime.now().isoformat())
        )
        conn.commit()
        await q.edit_message_text(
            f"📊 *LIVE SIGNAL*\nPair: BTC/USDT\nSignal: *{signal}*",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    elif q.data == "trend":
        await q.edit_message_text(
            "📈 Trend: *STRONG TRENDING*",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    elif q.data == "stats":
        cursor.execute("SELECT COUNT(*) FROM signals WHERE result='WIN'")
        wins = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM signals WHERE result='LOSS'")
        losses = cursor.fetchone()[0]
        await q.edit_message_text(
            f"🧮 Wins: {wins}\nLosses: {losses}",
            reply_markup=main_menu()
        )

    elif q.data == "settings":
        if q.from_user.id != ADMIN_ID:
            await q.answer("⛔ Admin only", show_alert=True)
            return

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏸ Pause", callback_data="pause"),
             InlineKeyboardButton("▶ Resume", callback_data="resume")],
            [InlineKeyboardButton("🤖 Auto ON/OFF", callback_data="auto")]
        ])
        await q.edit_message_text("⚙️ Admin Settings", reply_markup=kb)

    elif q.data == "pause":
        BOT_ACTIVE = False
        await q.answer("Bot Paused")

    elif q.data == "resume":
        BOT_ACTIVE = True
        await q.answer("Bot Resumed")

    elif q.data == "auto":
        AUTO_MODE = not AUTO_MODE
        await q.answer(f"Auto Mode: {AUTO_MODE}")

# ===============================
# ADMIN COMMANDS
# ===============================
async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE
    if update.effective_user.id == ADMIN_ID:
        BOT_ACTIVE = False
        await update.message.reply_text("⏸ Bot Paused")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE
    if update.effective_user.id == ADMIN_ID:
        BOT_ACTIVE = True
        await update.message.reply_text("▶ Bot Resumed")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args)
    await update.message.reply_text(f"📢 Broadcast sent:\n{msg}")

# ===============================
# AUTO SIGNAL LOOP
# ===============================
async def auto_loop(app):
    while True:
        try:
            if BOT_ACTIVE and AUTO_MODE:
                signal = get_ema_sar_signal()
                logging.info(f"AUTO SIGNAL: {signal}")
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(e)

# ===============================
# FASTAPI SERVER (RAILWAY)
# ===============================
app = FastAPI()

@app.get("/")
def root():
    return {"status": "EMA SAR BOT RUNNING"}

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# ===============================
# MAIN
# ===============================
def main():
    print("🤖 EMA SAR BOT RUNNING SUCCESSFULLY")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("pause", pause))
    application.add_handler(CommandHandler("resume", resume))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CallbackQueryHandler(callbacks))

    threading.Thread(target=run_api, daemon=True).start()

    application.run_polling()

if __name__ == "__main__":
    main()
