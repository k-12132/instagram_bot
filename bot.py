import os
from telegram.ext import Updater, CommandHandler

# جلب التوكن من متغيرات البيئة
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ لم يتم العثور على BOT_TOKEN في متغيرات البيئة")

# أمر /start
def start(update, context):
    update.message.reply_text("✅ البوت شغال 100% على Render (إصدار 13.15)!")

def main():
    # إنشاء Updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # إضافة الأوامر
    dp.add_handler(CommandHandler("start", start))

    # تشغيل البوت (Polling)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
