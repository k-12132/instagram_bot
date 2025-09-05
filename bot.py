import os
import instaloader
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# تحميل الفيديو من انستقرام
def download_instagram_video(url: str, filename: str) -> str:
    loader = instaloader.Instaloader()
    try:
        post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
        loader.download_post(post, target=filename)
        return filename
    except Exception as e:
        return str(e)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط فيديو من انستقرام وسأقوم بتحميله لك 📥")

# التعامل مع الروابط
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "instagram.com" in text:
        await update.message.reply_text("جاري التحميل ⏳...")

        filename = "downloaded_post"
        result = download_instagram_video(text, filename)

        if os.path.exists(filename):
            for file in os.listdir(filename):
                if file.endswith(".mp4"):
                    with open(os.path.join(filename, file), "rb") as video:
                        await update.message.reply_video(video)
            # تنظيف بعد الارسال
            for file in os.listdir(filename):
                os.remove(os.path.join(filename, file))
            os.rmdir(filename)
        else:
            await update.message.reply_text(f"خطأ: {result}")
    else:
        await update.message.reply_text("أرسل رابط فيديو من انستقرام فقط 📎")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("يجب وضع التوكن في متغير البيئة BOT_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
