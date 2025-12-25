import os
import uuid
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("https://api.telegram.org/bot<TOKEN>/getWebhookInfo")
BASE_URL = "https://all-in-one-tools-qhdb.onrender.com/files/"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to VideoPro Bot\n\n"
        "🎥 Send a video URL to start."
    )

# ---------------- URL HANDLER ----------------
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["url"] = update.message.text.strip()

    keyboard = [
        [InlineKeyboardButton("360p", callback_data="q_360"),
         InlineKeyboardButton("720p", callback_data="q_720")]
    ]

    await update.message.reply_text(
        "🎥 Select quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- QUALITY ----------------
async def quality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality = query.data.split("_")[1]
    url = context.user_data["url"]

    await query.message.reply_text("⏳ Downloading...")

    filename = await download_video(url, quality)
    link = BASE_URL + filename

    await query.message.reply_text(f"✅ Download ready:\n🔗 {link}")

# ---------------- DOWNLOAD ----------------
async def download_video(url, quality):
    uid = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, f"{uid}.%(ext)s")

    subprocess.run([
        "yt-dlp",
        "-f", f"bestvideo[height<={quality}]+bestaudio/best",
        "-o", output,
        url
    ])

    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(uid):
            return f

    raise Exception("Download failed")

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(quality_selected, pattern="^q_"))

    PORT = int(os.environ.get("PORT", 10000))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://all-in-one-tools-qhdb.onrender.com/webhook"
    )

if __name__ == "__main__":
    main()
