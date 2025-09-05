import os
import imghdr
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask

# اقرأ التوكن من متغير البيئة (Render يحفظه هناك)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# إعداد Flask (مطلوب لتشغيل Render)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("اهلا 👋 انا شغال 100%!")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
