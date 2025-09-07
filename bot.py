import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ----------------------------------------
# إعداد متغيرات البيئة
# ----------------------------------------
TOKEN = os.environ.get("BOT_TOKEN")  # ضع توكن البوت في Environment Variables
EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")  # Hostname من Render
PORT = int(os.environ.get("PORT", 8443))  # البورت من Render
DOWNLOAD_DIR = "downloads"  # مجلد التنزيلات

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ----------------------------------------
# دالة تحميل الفيديوهات
# ----------------------------------------
async def download_video(url: str):
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'format': 'best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.join(DOWNLOAD_DIR, f"{info['title']}.{info['ext']}")

# ----------------------------------------
# Handlers
# ----------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل رابط فيديو من TikTok، YouTube، أو Instagram لتحميله.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ جاري تحميل الفيديو...")
    try:
        filepath = await download_video(url)
        await update.message.reply_document(open(filepath, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

# ----------------------------------------
# إعداد التطبيق
# ----------------------------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ----------------------------------------
# تشغيل Webhook
# ----------------------------------------
if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{EXTERNAL_HOSTNAME}/{TOKEN}"
    )
