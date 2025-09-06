import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# جلب التوكن من متغير البيئة
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ لم يتم العثور على BOT_TOKEN في متغيرات البيئة")

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال 100% على Render!")

def main():
    # مافي Updater نهائياً
    app = Application.builder().token(TOKEN).build()

    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))

    # تشغيل البوت
    app.run_polling()

if __name__ == "__main__":
    main()
