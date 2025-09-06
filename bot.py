import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yt_dlp

# جلب التوكن من متغير البيئة
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ لم يتم العثور على BOT_TOKEN في متغيرات البيئة")

# مسار ملف الكوكيز
COOKIES_FILE = "cookies.txt"  # ضع هنا مسار ملف الكوكيز الخاص بك

# إعدادات yt-dlp
ydl_opts = {
    "format": "best",
    "outtmpl": "%(title)s.%(ext)s",
    "cookiefile": COOKIES_FILE,  # استخدام الكوكيز
    "noplaylist": True
}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال 100%! أرسل رابط Instagram أو YouTube لتحميل الفيديو.")

# أمر /download
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ أرسل رابط الفيديو بعد الأمر.")
        return

    url = context.args[0]
    msg = await update.message.reply_text("⏳ جاري تنزيل الفيديو...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_text(f"✅ تم تنزيل الفيديو: {filename}")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التنزيل:\n{e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))

    app.run_polling()

if __name__ == "__main__":
    main()
