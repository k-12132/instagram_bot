#!/usr/bin/env python3
import os
import logging
import tempfile
import asyncio
from urllib.parse import urlparse
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader
import requests

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Instaloader with session management
L = instaloader.Instaloader(
    sleep=True,
    quiet=True,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    request_timeout=60,
    max_connection_attempts=3
)
L.context.log = lambda *args, **kwargs: None  # Disable instaloader logs

class InstagramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued"""
        welcome_text = """
مرحباً! 👋

أنا بوت تحميل فيديوهات الإنستغرام
أرسل لي رابط فيديو أو منشور من الإنستغرام وسأقوم بتحميله لك

استخدم الأوامر التالية:
/start - بدء المحادثة
/help - عرض المساعدة

فقط أرسل رابط الإنستغرام وسأتولى الباقي! 📥
        """
        await update.message.reply_text(welcome_text)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued"""
        help_text = """
📋 كيفية الاستخدام:

1. انسخ رابط الفيديو من الإنستغرام
2. أرسل الرابط هنا
3. انتظر قليلاً حتى يتم تحميل الفيديو
4. ستحصل على الفيديو جاهز للتحميل!

📝 ملاحظات:
- يمكنني تحميل الفيديوهات والصور من المنشورات العامة فقط
- الحسابات الخاصة غير مدعومة
- أرسل رابط واحد في كل رسالة

💡 مثال على الرابط:
https://www.instagram.com/p/ABC123def/
        """
        await update.message.reply_text(help_text)

    def extract_shortcode(self, url):
        """Extract Instagram post shortcode from URL"""
        try:
            if 'instagram.com' not in url:
                return None
            
            # Handle different Instagram URL formats
            if '/p/' in url:
                shortcode = url.split('/p/')[1].split('/')[0].split('?')[0]
            elif '/reel/' in url:
                shortcode = url.split('/reel/')[1].split('/')[0].split('?')[0]
            else:
                return None
            
            return shortcode
        except:
            return None

    async def download_instagram_content(self, shortcode, max_retries=3):
        """Download Instagram post content with retry logic"""
        for attempt in range(max_retries):
            try:
                # Add delay between attempts
                if attempt > 0:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                
                # Download the post
                L.download_post(post, target=temp_dir)
                
                # Find downloaded files
                downloaded_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.mp4', '.jpg', '.jpeg', '.png')):
                            downloaded_files.append(os.path.join(root, file))
                
                return downloaded_files, post.caption if post.caption else ""
                
            except instaloader.exceptions.ConnectionException as e:
                error_msg = str(e).lower()
                if "403" in error_msg or "forbidden" in error_msg:
                    return None, "forbidden"
                elif "401" in error_msg or "unauthorized" in error_msg:
                    if attempt < max_retries - 1:
                        continue  # Retry for rate limiting
                    return None, "rate_limited"
                elif "404" in error_msg or "not found" in error_msg:
                    return None, "not_found"
                else:
                    if attempt < max_retries - 1:
                        continue
                    return None, "connection_error"
            except instaloader.exceptions.InstaloaderException as e:
                error_msg = str(e).lower()
                if "private" in error_msg:
                    return None, "private"
                elif "not exist" in error_msg or "not found" in error_msg:
                    return None, "not_found"
                else:
                    logger.error(f"Instaloader error: {e}")
                    return None, "instaloader_error"
            except Exception as e:
                logger.error(f"Unexpected error downloading Instagram content: {e}")
                if attempt < max_retries - 1:
                    continue
                return None, "unexpected_error"

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        if not update.message or not update.message.text:
            return
            
        message_text = update.message.text
        
        # Check if message contains Instagram URL
        if 'instagram.com' in message_text:
            await update.message.reply_text("🔄 جارٍ تحميل المحتوى... يرجى الانتظار")
            
            shortcode = self.extract_shortcode(message_text)
            if not shortcode:
                await update.message.reply_text("❌ رابط غير صحيح. تأكد من إرسال رابط إنستغرام صالح")
                return
            
            try:
                downloaded_files, error_type = await self.download_instagram_content(shortcode)
                
                if downloaded_files:
                    await update.message.reply_text(f"✅ تم التحميل بنجاح! يتم إرسال {len(downloaded_files)} ملف...")
                    
                    # Send each file
                    for file_path in downloaded_files:
                        if file_path.endswith('.mp4'):
                            with open(file_path, 'rb') as video:
                                await update.message.reply_video(
                                    video=video,
                                    caption=f"📹 فيديو من الإنستغرام\n\n{error_type[:100]}..." if error_type else "📹 فيديو من الإنستغرام"
                                )
                        else:
                            with open(file_path, 'rb') as photo:
                                await update.message.reply_photo(
                                    photo=photo,
                                    caption=f"📷 صورة من الإنستغرام\n\n{error_type[:100]}..." if error_type else "📷 صورة من الإنستغرام"
                                )
                    
                    # Clean up temporary files
                    import shutil
                    shutil.rmtree(os.path.dirname(downloaded_files[0]), ignore_errors=True)
                else:
                    # Handle specific error types
                    if error_type == "forbidden":
                        await update.message.reply_text("🚫 الإنستغرام يحظر الوصول حالياً. جرب مرة أخرى بعد قليل")
                    elif error_type == "rate_limited":
                        await update.message.reply_text("⏰ تم تجاوز الحد المسموح من الطلبات. يرجى الانتظار 5-10 دقائق ثم المحاولة مرة أخرى")
                    elif error_type == "private":
                        await update.message.reply_text("🔒 هذا المنشور من حساب خاص. لا يمكنني تحميل محتوى من الحسابات الخاصة")
                    elif error_type == "not_found":
                        await update.message.reply_text("❓ المنشور غير موجود أو تم حذفه. تأكد من الرابط")
                    elif error_type == "connection_error":
                        await update.message.reply_text("🌐 مشكلة في الاتصال بالإنستغرام. جرب مرة أخرى")
                    else:
                        await update.message.reply_text("❌ فشل في تحميل المحتوى. تأكد من أن الرابط صحيح والمنشور متاح للعامة")
                
            except Exception as e:
                logger.error(f"Error processing Instagram URL: {e}")
                await update.message.reply_text("❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى")
        
        else:
            await update.message.reply_text("📎 أرسل رابط إنستغرام لتحميل المحتوى\nاستخدم /help للمساعدة")

    def run(self):
        """Start the bot"""
        logger.info("Starting Instagram downloader bot...")
        self.application.run_polling()

def main():
    # Get bot token from environment variable
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ خطأ: لم يتم العثور على TELEGRAM_BOT_TOKEN")
        print("يرجى إضافة رمز البوت في ملف .env")
        return
    
    # Create and run bot
    bot = InstagramBot(bot_token)
    bot.run()

if __name__ == '__main__':
    main()
