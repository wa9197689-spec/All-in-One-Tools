import os
import uuid
import subprocess
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8556741893:AAGS-ZNqsqNBYuRLXGI8URWAdXTekdUNBY0"
BASE_URL = "https://all-in-one-tools-qhdb.onrender.com/files/video.mp4"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to VideoPro Bot\n\n"
        "🎥 Download videos from YouTube, Instagram, Facebook, TikTok & more.\n\n"
        "⚙️ Features:\n"
        "• Multiple quality options\n"
        "• Optional audio & subtitles\n"
        "• Fast direct download links\n\n"
        "📌 Send a video URL to get started.\n\n"
        "⚠️ Personal & educational use only."
    )

# ---------------- URL HANDLER ----------------
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["url"] = url

    keyboard = [
        [InlineKeyboardButton("144p", callback_data="q_144"),
         InlineKeyboardButton("240p", callback_data="q_240")],
        [InlineKeyboardButton("360p", callback_data="q_360"),
         InlineKeyboardButton("480p", callback_data="q_480")],
        [InlineKeyboardButton("720p", callback_data="q_720"),
         InlineKeyboardButton("1080p", callback_data="q_1080")]
    ]

    await update.message.reply_text(
        "🎥 Select video quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- QUALITY ----------------
async def quality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality = query.data.split("_")[1]
    context.user_data["quality"] = quality

    keyboard = [
        [InlineKeyboardButton("✅ Audio + Subtitles + Translate", callback_data="extra_yes")],
        [InlineKeyboardButton("❌ Only Video", callback_data="extra_no")]
    ]

    await query.message.reply_text(
        "⚙️ Do you want extra features?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- EXTRA SYSTEM ----------------
async def extra_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    extras = query.data == "extra_yes"
    context.user_data["extras"] = extras

    await query.message.reply_text("⏳ Processing your video, please wait...")

    url = context.user_data["url"]
    quality = context.user_data["quality"]

    filename = await download_video(url, quality, extras)
    download_link = BASE_URL + filename

    await query.message.reply_text(
        f"✅ Your download is ready:\n\n🔗 {download_link}"
    )

# ---------------- DOWNLOAD LOGIC ----------------
async def download_video(url, quality, extras):
    uid = str(uuid.uuid4())

    output_template = os.path.join(DOWNLOAD_DIR, f"{uid}.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", f"bestvideo[height<={quality}]+bestaudio/best",
        "-o", output_template,
        url
    ]
    subprocess.run(cmd)

    # 🔍 Find actual downloaded file
    for file in os.listdir(DOWNLOAD_DIR):
        if file.startswith(uid):
            video_file = file
            video_path = os.path.join(DOWNLOAD_DIR, file)
            break
    else:
        raise Exception("Download failed")

    if extras:
        audio_path = os.path.join(DOWNLOAD_DIR, f"{uid}.mp3")
        subprocess.run(["ffmpeg", "-i", video_path, audio_path])

    return video_file


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(quality_selected, pattern="^q_"))
    app.add_handler(CallbackQueryHandler(extra_selected, pattern="^extra_"))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
