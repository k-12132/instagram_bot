import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# جلب التوكن من متغير البيئة
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في المتغيرات")

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً! أرسل رابط الفيديو من تيك توك أو يوتيوب وسأنزله لك.")

# معالجة الروابط
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # خيارات yt-dlp
    ydl_opts = {
        "format": "best",
        "outtmpl": "video.%(ext)s"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # إرسال الفيديو
        await update.message.reply_video(video=open(file_path, "rb"))

        # حذف الملف بعد الإرسال
        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()

    # أوامر
    app.add_handler(CommandHandler("start", start))

    # استقبال أي رسالة (رابط فيديو)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
