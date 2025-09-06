import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yt_dlp

# جلب التوكن من متغير البيئة
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ لم يتم العثور على BOT_TOKEN في متغيرات البيئة")

# خيارات yt-dlp
YDL_OPTIONS = {
    "outtmpl": "%(title)s.%(ext)s",  # اسم الملف
    "format": "best",
    "cookiefile": "cookies.txt"      # ملف الكوكيز
}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال 100% على Render!")

# أمر /download <رابط>
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❌ أرسل رابط الفيديو بعد الأمر.")
        return

    url = context.args[0]
    await update.message.reply_text(f"⏳ جاري تنزيل الفيديو من: {url}")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_text(f"✅ تم تنزيل الفيديو: {filename}")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))
    app.run_polling()

if __name__ == "__main__":
    main()
