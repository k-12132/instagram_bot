# bot.py
import os
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")  # ضع توكن البوت في متغير بيئة

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! هذا البوت جاهز للعمل 🔥")

# مثال على أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("يمكنك إرسال أي رسالة لأخذ استجابة!")

# استقبال أي رسالة نصية
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # مثال على استخدام ChatAction
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text(f"لقد قلت: {update.message.text}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    # تشغيل البوت
    app.run_polling()

if __name__ == "__main__":
    main()
