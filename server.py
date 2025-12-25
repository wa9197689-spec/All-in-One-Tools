from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

DOWNLOAD_DIR = "downloads"

# Serve files directly
app.mount("/files", StaticFiles(directory=DOWNLOAD_DIR), name="files")

@app.get("/")
def home():
    return {"status": "Server running"}

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
