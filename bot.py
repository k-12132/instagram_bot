import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# حل مشكلة imghdr في بعض البيئات
try:
    import imghdr
except ModuleNotFoundError:
    import types, sys
    sys.modules['imghdr'] = types.ModuleType('imghdr')

TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))
HOST = "0.0.0.0"
WEBHOOK_URL = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بوت يوتيوب جاهز ✅\nأرسل رابط فيديو لتحميله.")

async def download_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("الرجاء إرسال رابط فيديو صحيح.")
        return

    await update.message.reply_text("جاري التحميل ... ⏳")

    ydl_opts = {
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "noplaylist": True,
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)

        if os.path.getsize(filename) < 50 * 1024 * 1024:
            await update.message.reply_video(video=open(filename, "rb"))
        else:
            await update.message.reply_text(f"تم تحميل الفيديو: {filename}\nلكن الحجم أكبر من 50MB، لا يمكن إرساله مباشرة.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {str(e)}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_youtube))

if __name__ == "__main__":
    app.run_webhook(
        listen=HOST,
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )
