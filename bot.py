import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = f"https://<اسم-خدمتك>.onrender.com/{TOKEN}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! البوت يعمل بنجاح ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"لقد أرسلت: {update.message.text}")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # تشغيل Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_path=f"/{TOKEN}",
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )
