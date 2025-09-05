import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# جلب التوكن من متغير البيئة
token = os.environ.get("BOT_TOKEN")
if not token:
    raise ValueError("يجب وضع التوكن في متغير البيئة BOT_TOKEN")

# أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبا! البوت يعمل بنجاح.")

# الدالة الرئيسية لتشغيل البوت
def main():
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()  # تشغيل البوت

if __name__ == "__main__":
    main()
