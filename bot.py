from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os

# التوكن حق البوت
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# تعريف أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أنا بوتك جاهز للعمل.")

# مثال على الرد على أي رسالة نصية
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"لقد أرسلت: {update.message.text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Webhook setup
    # هذا الرابط يكون رابط الخدمة على Render + مسار endpoint
    WEBHOOK_URL = f"https://<اسم-خدمتك>.onrender.com/{BOT_TOKEN}"

    # إزالة أي webhook قديم
    import asyncio
    asyncio.run(app.bot.delete_webhook())
    
    # ضبط webhook
    asyncio.run(app.bot.set_webhook(WEBHOOK_URL))

    # تشغيل الخدمة
    # على Render نستخدم run_polling=False لأنه webhook
    app.run_webhook(listen="0.0.0.0",
                    port=int(os.environ.get("PORT", 10000)),
                    webhook_path=f"/{BOT_TOKEN}")
