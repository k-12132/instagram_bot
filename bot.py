import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

token = os.environ.get("BOT_TOKEN")
if not token:
    raise ValueError("يجب وضع التوكن في متغير البيئة BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبا! البوت يعمل بنجاح.")

def main():
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
