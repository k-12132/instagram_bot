import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import filetype

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التوكن من ملف .env
BOT_TOKEN = os.getenv("BOT_TOKEN")

# إعداد اللوقز
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# دالة البدء
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط وسأحمله لك 🚀")

# دالة تحميل (مثال مبسط)
async def download(update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text(f"جاري التحميل من: {url}")

    # هنا تقدر تستخدم requests لتحميل المحتوى أو أي مكتبة ثانية
    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            kind = filetype.guess(r.content)
            if kind:
                await update.message.reply_text(f"الملف نوعه: {kind.mime}")
            else:
                await update.message.reply_text("ما قدرت أحدد نوع الملف.")
        else:
            await update.message.reply_text("الرابط غير صالح ❌")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# تشغيل البوت
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    app.run_polling()
