# bot.py
import os
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# قراءة التوكن من متغير البيئة
TOKEN = os.getenv("TOKEN")

# ----- الأوامر -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! هذا البوت جاهز للعمل 🔥")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("يمكنك إرسال أي رسالة لأخذ استجابة!")

# ----- استقبال أي رسالة -----
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إرسال Action قبل الرد
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    # مثال على الرد
    await update.message.reply_text(f"لقد قلت: {update.message.text}")

# ----- الدالة الرئيسية -----
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    # تشغيل البوت
    app.run_polling()

# ----- تنفيذ البوت -----
if __name__ == "__main__":
    main()
