from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

DOWNLOAD_DIR = "downloads"

# ✅ Ensure downloads folder exists (IMPORTANT)
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# ✅ Serve files
app.mount("/files", StaticFiles(directory=DOWNLOAD_DIR), name="files")

# ✅ ROOT + HEAD FIX (UptimeRobot issue solved)
@app.get("/")
@app.head("/")
def home():
    return {"status": "Server running"}

# ✅ Download endpoint
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
