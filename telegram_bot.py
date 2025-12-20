# =========================================================
# TradeWin Telegram Bot – FINAL FIXED VERSION
# =========================================================

import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# ================= CONFIG =================

BOT_TOKEN = "8398066628:AAESaP_0F54Grcya9-JP8M2b-DcoSxWi73o"

# ✅ USE YOUR RAILWAY PUBLIC URL (HTTPS ONLY)
API_URL = "https://web-production-8c4fbe.up.railway.app/api/binary/signal"

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *TradeWin Bot Active*\n\n"
        "Commands:\n"
        "/signal – Get EMA + SAR Signal",
        parse_mode="Markdown"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # 🔒 Stable request (NO httpx)
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        message = (
            "📊 *TradeWin Signal*\n\n"
            f"Pair: {data.get('pair')}\n"
            f"Timeframe: {data.get('timeframe')}\n"
            f"Signal: *{data.get('signal')}*\n"
            f"Confidence: {data.get('confidence')}%\n"
            f"Strategy: {data.get('strategy')}"
        )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "⚠️ Server timeout.\nPlease try again in a few seconds."
        )

    except requests.exceptions.RequestException:
        await update.message.reply_text(
            "❌ Unable to connect to signal server.\nCheck backend status."
        )

# ================= MAIN =================

def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))

    print("🤖 TradeWin Telegram Bot Running...")
    app.run_polling(drop_pending_updates=True)

# ================= RUN =================

if __name__ == "__main__":
    main()
