#!/usr/bin/env python3
import os
import logging
import tempfile
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader
import shutil

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Instaloader
L = instaloader.Instaloader(
    sleep=True,
    quiet=True,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    request_timeout=60,
    max_connection_attempts=3
)
L.context.log = lambda *args, **kwargs: None  # Disable instaloader logs

# Telegram upload limits
MAX_PHOTO_SIZE = 50 * 1024 * 1024    # 50MB
MAX_VIDEO_SIZE = 2000 * 1024 * 1024  # 2GB

class InstagramBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "مرحباً 👋\n\n"
            "أنا بوت تحميل فيديوهات وصور إنستغرام.\n"
            "أرسل رابط أي منشور وسأقوم بتحميله لك 📥\n\n"
            "استخدم /help لمعرفة التفاصيل."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📋 طريقة الاستخدام:\n\n"
            "1️⃣ انسخ رابط المنشور من إنستغرام\n"
            "2️⃣ أرسله هنا\n"
            "3️⃣ انتظر قليلاً وسيصلك المحتوى ✅\n\n"
            "⚠️ ملاحظات:\n"
            "- يدعم المنشورات العامة فقط\n"
            "- الحسابات الخاصة غير مدعومة\n"
            "- حد حجم الملفات: الصور 50MB والفيديوهات 2GB\n\n"
            "مثال على رابط: https://www.instagram.com/p/ABC123/"
        )

    def extract_shortcode(self, url):
        try:
            if 'instagram.com' not in url:
                return None
            if '/p/' in url:
                return url.split('/p/')[1].split('/')[0].split('?')[0]
            elif '/reel/' in url:
                return url.split('/reel/')[1].split('/')[0].split('?')[0]
            return None
        except:
            return None

    async def download_instagram_content(self, shortcode, max_retries=3):
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    await asyncio.sleep(2 ** attempt)

                post = instaloader.Post.from_shortcode(L.context, shortcode)
                temp_dir = tempfile.mkdtemp()
                L.download_post(post, target=temp_dir)

                downloaded_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.mp4', '.jpg', '.jpeg', '.png')):
                            downloaded_files.append(os.path.join(root, file))

                return downloaded_files, post.caption or ""
            except Exception as e:
                logger.error(f"Download error: {e}")
                if attempt < max_retries - 1:
                    continue
                return None, str(e)
        return None, "unknown_error"

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        url = update.message.text.strip()

        if "instagram.com" not in url:
            await update.message.reply_text("📎 أرسل رابط إنستغرام صالح\nاستخدم /help للمساعدة.")
            return

        await update.message.reply_text("⏳ جارٍ التحميل...")

        shortcode = self.extract_shortcode(url)
        if not shortcode:
            await update.message.reply_text("❌ رابط غير صحيح.")
            return

        files, caption = await self.download_instagram_content(shortcode)
        if not files:
            await update.message.reply_text("🚫 فشل التحميل. الرابط غير صالح أو الحساب خاص.")
            return

        try:
            for file_path in files:
                file_size = os.path.getsize(file_path)

                if file_path.endswith('.mp4'):
                    if file_size > MAX_VIDEO_SIZE:
                        await update.message.reply_text("⚠️ الفيديو أكبر من الحد المسموح (2GB).")
                        continue
                    with open(file_path, 'rb') as video:
                        await update.message.reply_video(video=video, caption=caption[:1000] or "🎬 فيديو من إنستغرام")
                else:
                    if file_size > MAX_PHOTO_SIZE:
                        await update.message.reply_text("⚠️ الصورة أكبر من الحد المسموح (50MB).")
                        continue
                    with open(file_path, 'rb') as photo:
                        await update.message.reply_photo(photo=photo, caption=caption[:1000] or "📷 صورة من إنستغرام")

        except Exception as e:
            logger.error(f"Send error: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء إرسال الملفات.")
        finally:
            if files:
                shutil.rmtree(os.path.dirname(files[0]), ignore_errors=True)

    def run(self):
        logger.info("Bot is running...")
        self.application.run_polling()

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ ضع TELEGRAM_BOT_TOKEN في ملف .env")
        return
    bot = InstagramBot(token)
    bot.run()

if __name__ == "__main__":
    main()
