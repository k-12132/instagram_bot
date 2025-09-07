import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from urllib.parse import quote_plus

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
WEBHOOK_URL = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "بوت التحميل جاهز ✅\n"
        "أرسل رابط فيديو من: تيك توك، إنستقرام، أو يوتيوب."
    )

# دالة التحميل مع دعم الفيديوهات الكبيرة
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("الرجاء إرسال رابط فيديو صحيح.")
        return

    await update.message.reply_text("جاري التحميل ... ⏳")

    ydl_opts = {
        "format": "best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "noplaylist": True,
        "overwrites": True,
        # لدعم حسابات خاصة على إنستقرام
        # "username": "INSTAGRAM_USERNAME",
        # "password": "INSTAGRAM_PASSWORD",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)

        filesize = os.path.getsize(filename)
        if filesize < 50 * 1024 * 1024:
            await update.message.reply_video(video=open(filename, "rb"))
            os.remove(filename)  # حذف الملف بعد الإرسال
        else:
            # إرسال رابط تنزيل مباشر للمستخدم
            download_link = f"{os.environ['RENDER_EXTERNAL_HOSTNAME']}/downloads/{quote_plus(os.path.basename(filename))}"
            await update.message.reply_text(
                f"تم تحميل الفيديو بنجاح ✅\nحجم الفيديو أكبر من 50MB، يمكن تنزيله من الرابط التالي:\n{download_link}"
            )
            # الملف يبقى على السيرفر ويمكن عمل جدولة لحذفه لاحقًا

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء التحميل: {str(e)}")

# إنشاء التطبيق
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

# تشغيل Webhook
if __name__ == "__main__":
    app.run_webhook(
        listen=HOST,
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )
