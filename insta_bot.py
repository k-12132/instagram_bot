import os
import re
import json
import threading
import logging
import requests
from datetime import datetime
from instaloader import Instaloader, Post
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Logger setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Instaloader setup
loader = Instaloader()
SESSION_FILE = f"session-{USERNAME}"

if os.path.exists(SESSION_FILE):
    loader.load_session_from_file(USERNAME, filename=SESSION_FILE)
else:
    loader.login(USERNAME, PASSWORD)
    loader.save_session_to_file(SESSION_FILE)

# Admin & users log
USERS_LOG_FILE = "users.log"

def log_user(user):
    user_data = {"id": user.id, "username": user.username, "first_name": user.first_name,
                 "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    users = []
    if os.path.exists(USERS_LOG_FILE):
        with open(USERS_LOG_FILE, "r") as f:
            users = json.load(f)
    users.append(user_data)
    with open(USERS_LOG_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Helpers
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

def fetch_instagram_media(url):
    shortcode = extract_shortcode(url)
    if not shortcode:
        return None
    post = Post.from_shortcode(loader.context, shortcode)
    return post.video_url if post.is_video else post.url

# Commands
def start(update, context):
    user = update.effective_user
    log_user(user)
    update.message.reply_text(
        "👋 مرحبًا! أرسل لي رابط إنستغرام (Post / Reel / IGTV) وسأرسل لك الوسائط مباشرة."
    )

def download(update, context):
    thread = threading.Thread(target=process_download, args=(update, context))
    thread.start()

def process_download(update, context):
    user = update.effective_user
    log_user(user)
    url = update.message.text.strip()
    update.message.reply_chat_action(ChatAction.TYPING)

    media_url = fetch_instagram_media(url)
    if not media_url:
        update.message.reply_text("❌ الرابط غير صالح أو المحتوى خاص.")
        return

    file_name = f"temp_{user.id}.mp4" if "video" in media_url else f"temp_{user.id}.jpg"
    try:
        r = requests.get(media_url, stream=True)
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        with open(file_name, "rb") as f:
            if "video" in media_url:
                context.bot.send_video(chat_id=update.message.chat_id, video=f)
            else:
                context.bot.send_photo(chat_id=update.message.chat_id, photo=f)
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# Main
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download))
    updater.start_polling()
    logging.info("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
