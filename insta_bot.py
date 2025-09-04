import os
import instaloader
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("⚠️ ضع TELEGRAM_TOKEN في ملف .env")

# إعداد instaloader
loader = instaloader.Instaloader()

# دالة الترحيب
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 أهلاً! أرسل لي رابط منشور أو ريل من إنستقرام وسأحاول تحميله لك.")

# دالة التحميل
def download_instagram(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    update.message.reply_text("⏳ جاري التحميل...")

    try:
        shortcode = url.split("/")[-2]  # استخراج الـ shortcode من الرابط
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.is_video:
            video_url = post.video_url
            context.bot.send_video(chat_id=chat_id, video=video_url, caption="✅ تم التحميل بنجاح")
        else:
            context.bot.send_photo(chat_id=chat_id, photo=post.url, caption="✅ تم التحميل بنجاح")

    except Exception as e:
        update.message.reply_text(f"❌ لم أستطع استخراج الوسائط. ({str(e)})")

# تشغيل البوت
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_instagram))

updater.start_polling()
updater.idle()
