import os
import re
import json
import threading
from datetime import datetime

import pytz
import requests
from instaloader import Instaloader, Post
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TASHKENT_TZ = pytz.timezone("Asia/Tashkent")

# Load environment variables
load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Instagram credentials
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# File paths
USERS_LOG_FILE = "users.log"
ADMIN_FILE = "admin.json"

# Instaloader setup
loader = Instaloader()
SESSION_FILE = f"{os.getcwd()}/session-{USERNAME}"
session_lock = threading.Lock()

def load_or_create_session():
    with session_lock:
        if os.path.exists(SESSION_FILE):
            loader.load_session_from_file(USERNAME, filename=SESSION_FILE)
        else:
            loader.login(USERNAME, PASSWORD)
            loader.save_session_to_file(SESSION_FILE)

load_or_create_session()

# Admin functions
def get_admin():
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r") as file:
            return json.load(file).get("admin_id")
    return None

def set_admin(user_id):
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "w") as file:
            json.dump({"admin_id": user_id}, file)

# User logging
def log_user_data(user):
    server_time = datetime.now()
    tashkent_time = server_time.astimezone(TASHKENT_TZ)
    user_data = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "timestamp": tashkent_time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        if os.path.exists(USERS_LOG_FILE):
            with open(USERS_LOG_FILE, "r") as file:
                users = json.load(file)
        else:
            users = []

        for existing_user in users:
            if existing_user["user_id"] == user_data["user_id"]:
                existing_user["timestamp"] = user_data["timestamp"]
                break
        else:
            users.append(user_data)

        with open(USERS_LOG_FILE, "w") as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        print(f"Error logging user data: {e}")

# List users command
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin_id = get_admin()
    if user.id != admin_id:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    try:
        if os.path.exists(USERS_LOG_FILE):
            with open(USERS_LOG_FILE, "r") as file:
                users = json.load(file)
            if not users:
                await update.message.reply_text("No users have used the bot yet.")
                return

            total_users = len(users)
            today_users = sum(
                1 for u in users if datetime.strptime(u['timestamp'], "%Y-%m-%d %H:%M:%S").date() == datetime.now(TASHKENT_TZ).date()
            )

            response = f"📊 Total users: {total_users}\n🌍 Users today: {today_users}\n\n📋 Users list:\n"
            for u in users:
                response += (
                    f"👤 User ID: {u['user_id']}\n"
                    f"   Username: @{u['username'] or 'N/A'}\n"
                    f"   First Name: {u['first_name']}\n"
                    f"   Last Active: {u['timestamp']}\n\n"
                )
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("No user log file found. No users have used the bot yet.")
    except Exception as e:
        print(f"Error reading user log file: {e}")
        await update.message.reply_text("⚠️ An error occurred while retrieving user data.")

# Instagram helper functions
def extract_shortcode(instagram_post):
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?#&]+)", instagram_post)
    return match.group(1) if match else None

def is_valid_instagram_url(url):
    return bool(re.match(r"https?://(www\.)?instagram\.com/(p|reel|tv)/", url))

def fetch_instagram_data(instagram_post):
    shortcode = extract_shortcode(instagram_post)
    if not shortcode:
        return None
    try:
        post = Post.from_shortcode(loader.context, shortcode)
        return post.video_url if post.is_video else post.url
    except Exception as e:
        print(f"Error fetching Instagram data: {e}")
        return None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_data(user)

    if get_admin() is None:
        set_admin(user.id)
        await update.message.reply_text("👑 You have been set as the admin!")

    await update.message.reply_text(
        "👋 Welcome to the Instagram Saver Bot!\n\n"
        "📩 Send me any **public** Instagram link (post, reel, or IGTV), and I'll fetch the media for you.\n"
        "⚠️ Make sure the post is **public** and not private.\n\n"
        "Happy downloading! 🎉"
    )

# Download handler
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_data(user)

    instagram_post = update.message.text.strip()
    if not is_valid_instagram_url(instagram_post):
        await update.message.reply_text("❌ Invalid Instagram URL. Please send a valid post, Reel, or IGTV link.")
        return

    await update.message.chat.send_action(action=constants.ChatAction.TYPING)
    progress_message = await update.message.reply_text("⏳ Fetching your media...")

    media_url = fetch_instagram_data(instagram_post)
    if not media_url:
        await progress_message.edit_text("❌ Failed to fetch media. Ensure the post is public and try again.")
        return

    file_name = f"temp_{update.message.chat_id}.mp4" if "video" in media_url else f"temp_{update.message.chat_id}.jpg"
    try:
        response = requests.get(media_url, stream=True)
        response.raise_for_status()
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        with open(file_name, "rb") as file:
            if "video" in media_url:
                await context.bot.send_video(chat_id=update.message.chat_id, video=file, caption="👾 Powered by @Instasave_downloader_bot")
            else:
                await context.bot.send_photo(chat_id=update.message.chat_id, photo=file, caption="👾 Powered by @Instasave_downloader_bot")

        await progress_message.delete()
    except Exception as e:
        print(f"Error sending media: {e}")
        await progress_message.edit_text("❌ Failed to send media. Please try again later.")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", list_users))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
