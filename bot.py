import os
import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------------------
# وظائف البوت
# ---------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! البوت يعمل ✅")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("يمكنك إرسال رابط حساب انستجرام لتحميل الستوري.")

async def download_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("أرسل رابط الحساب بعد الأمر، مثلا: /story username")
        return

    username = context.args[0]
    loader = instaloader.Instaloader()
    
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        stories = loader.get_stories(userids=[profile.userid])
        
        count = 0
        for story in stories:
            for item in story.get_items():
                loader.download_storyitem(item, f"downloads/{username}")
                count += 1
        
        if count == 0:
            await update.message.reply_text(f"لا توجد ستوريات لـ {username}.")
        else:
            await update.message.reply_text(f"تم تحميل {count} ستوري من {username}.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# ---------------------------
# دالة البداية
# ---------------------------

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("يجب وضع التوكن في متغير البيئة BOT_TOKEN")

    app = Application.builder().token(token).build()

    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("story", download_story))

    # تشغيل البوت
    app.run_polling()

if __name__ == "__main__":
    main()
