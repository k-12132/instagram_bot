import logging
import os
import re
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # تم تغيير Filters إلى filters
from instaloader import Instaloader, Post

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تهيئة محمل إنستقرام
L = Instaloader()

# دالة لمعالجة الأمر /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'مرحبًا {user.mention_markdown_v2()}\! أرسل لي رابط فيديو من إنستقرام وسأحاول تنزيله لك\.'
    )

# دالة لمعالجة رسائل المستخدم
async def handle_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    chat_id = update.message.chat_id
    
    # البحث عن رابط إنستقرام في النص
    insta_regex = r'(https?://(?:www\.)?instagram\.com/(?:p|reel|stories)/([^/?#&]+))'
    match = re.search(insta_regex, message_text)
    
    if match:
        post_url = match.group(1)
        await update.message.reply_text("جاري محاولة تنزيل الفيديو...")
        
        try:
            # الحصول على المنشور من إنستقرام
            shortcode = match.group(2)
            post = Post.from_shortcode(L.context, shortcode)
            
            # التأكد من أن المنشور يحتوي على فيديو
            if post.is_video:
                # إنشاء مجلد مؤقت
                temp_dir = f"temp_{chat_id}_{shortcode}"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # تنزيل الفيديو
                L.download_post(post, target=temp_dir)
                
                # البحث عن ملف الفيديو الذي تم تنزيله
                video_file = None
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp4'):
                        video_file = os.path.join(temp_dir, file)
                        break
                
                if video_file:
                    # إرسال الفيديو للمستخدم
                    with open(video_file, 'rb') as video:
                        await update.message.reply_video(
                            video=video, 
                            caption="تم التنزيل بنجاح!",
                            supports_streaming=True
                        )
                    
                    # حذف الملفات المؤقتة
                    os.remove(video_file)
                    os.rmdir(temp_dir)
                else:
                    await update.message.reply_text("لم يتم العثور على الفيديو بعد التنزيل.")
            else:
                await update.message.reply_text("المنشور المطلوب ليس فيديو.")
                
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text("عذرًا، حدث خطأ أثناء محاولة تنزيل الفيديو. قد يكون الرابط غير صحيح أو المحتوى خاص.")
    else:
        await update.message.reply_text("يرجى إرسال رابط فيديو إنستقرام صحيح. مثال: https://www.instagram.com/reel/CrY2HZtD/")

# دالة لمعالجة الأخطاء
async def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# الدالة الرئيسية
def main():
    # الحصول على التوكن من متغير البيئة أو استخدام قيمة افتراضية للتجربة
    TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
    
    if TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
        logger.error("لم يتم تعيين رمز البوت. يرجى تعيين متغير البيئة BOT_TOKEN.")
        return
    
    # إنشاء Application بدلاً من Updater (في الإصدارات الجديدة)
    from telegram.ext import Application
    application = Application.builder().token(TOKEN).build()

    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # بدء البوت
    application.run_polling()
    logger.info("بدأ البوت في الاستماع للرسائل...")

if __name__ == '__main__':
    main()
