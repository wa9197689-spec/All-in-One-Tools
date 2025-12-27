import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from telegram import Update
from telegram.ext import Application

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================= FASTAPI =================
app = FastAPI()

app.mount("/files", StaticFiles(directory=DOWNLOAD_DIR), name="files")

@app.get("/")
@app.head("/")
def home():
    return {"status": "Server running"}

# ================= TELEGRAM =================
telegram_app = Application.builder().token(BOT_TOKEN).build()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# ================= DOWNLOAD =================
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    return FileResponse(file_path)
