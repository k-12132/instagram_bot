import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ حل مشكلة imghdr في بعض البيئات القديمة
try:
    import imghdr
except ModuleNotFoundError:
    import types, sys
    sys.modules['imghdr'] = types.ModuleType('imghdr')

# التوكن
TOKEN = os.environ.get("BOT_TOKEN")

# إعدادات Webhook
PORT = int(os.environ.get("PORT", 8443))
HOST = "0.0.0.0"
WEBHOOK_URL = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بوتك يعمل ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"لقد أرسلت: {update.message.text}")

# إنشاء التطبيق
app = Application.builder().token(TOKEN).build()

# إضافة Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# تشغيل Webhook
if __name__ == "__main__":
    app.run_webhook(
        listen=HOST,
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )
