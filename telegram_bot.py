# =========================================================
# TradeWin PRO – Telegram Bot
# Olymp Trade EMA + SAR Signals
# =========================================================

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ================= CONFIG =================
BOT_TOKEN = "8398066628:AAESaP_0F54Grcya9-JP8M2b-DcoSxWi73o"
API_URL = "http://127.0.0.1:8000"  # change after Railway deploy

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📈 Get Signal", callback_data="get_signal")],
        [InlineKeyboardButton("📊 Open Dashboard", url="http://127.0.0.1:8000")]
    ]

    await update.message.reply_text(
        "🚀 *TradeWin PRO*\n\nOlymp Trade EMA + SAR Signals\n\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_signal":
        try:
            res = requests.get(f"{API_URL}/api/binary/signal", timeout=5)
            data = res.json()

            signal = data["signal"]
            confidence = data["confidence"]

            if signal == "WAIT":
                msg = "⏳ *No Trade Now*\nMarket not clear."
            else:
                msg = (
                    f"📊 *Olymp Trade Signal*\n\n"
                    f"📈 Signal: *{signal}*\n"
                    f"⏱ Timeframe: 1 Minute\n"
                    f"🎯 Strategy: EMA + SAR\n"
                    f"🔥 Confidence: *{confidence}%*"
                )

            await query.edit_message_text(msg, parse_mode="Markdown")

        except Exception as e:
            await query.edit_message_text(
                f"❌ Error fetching signal\n`{e}`",
                parse_mode="Markdown"
            )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 TradeWin Telegram Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
