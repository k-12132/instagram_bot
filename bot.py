import os
import yt_dlp
from urllib.parse import quote_plus
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from threading import Thread
import uvicorn

# حل مشكلة imghdr في بعض البيئات
try:
    import imghdr
except ModuleNotFoundError:
    import types, sys
    sys.modules['imghdr'] = types.ModuleType('imghdr')

# إعدادات البوت
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))
HOST = "0.0.0.0"
EXTERNAL_HOSTNAME = os.environ['RENDER_EXTERNAL_HOSTNAME']

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Middleware CORS
middleware = [Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'])]

# تطبيق Starlette لتقديم الملفات الكبيرة
web_app = Starlette(debug=True, middleware=middleware)
web_app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIR), name="downloads")

# --- أوامر البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "بوت التحميل جاهز ✅\n"
        "أرسل رابط فيديو من: تيك توك، إنستقرام (عام/خاص/Reels)، أو يوتيوب."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("الرجاء إرسال رابط فيديو صحيح.")
        return

    await update.message.reply_text("⏳ جاري التحميل ...")

    ydl_opts = {
        "format": "best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "noplaylist": True,
        "overwrites": True,
        # دعم إنستقرام الخاص
        "username": os.environ.get("IG_USERNAME"),
        "password": os.environ.get("IG_PASSWORD"),
        "extract_flat": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)

        filesize = os.path.getsize(filename)
        if filesize < 50 * 1024 * 1024:
            await update.message.reply_video(video=open(filename, "rb"))
            os.remove(filename)
        else:
            download_link = f"https://{EXTERNAL_HOSTNAME}/downloads/{quote_plus(os.path.basename(filename))}"
            await update.message.reply_text(
                f"✅ تم تحميل الفيديو بنجاح!\n"
                f"حجم الفيديو أكبر من 50MB، يمكن تنزيله من الرابط:\n{download_link}"
            )

    except yt_dlp.utils.DownloadError as e:
        await update.message.reply_text(
            f"❌ حدث خطأ أثناء التحميل.\n"
            f"السبب غالبًا أن الرابط غير عام أو الفيديو خاص. \n"
            f"تفاصيل: {str(e)}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌_
