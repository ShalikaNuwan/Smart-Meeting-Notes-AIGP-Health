import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Annotated

app = FastAPI()

UPLOAD_DIRECTORY = "./uploads"
ALLOWED_CONTENT_TYPES = ["audio/mpeg", "audio/x-m4a", "audio/wav"]
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Endpoint to upload audio files
@app.post("/upload-audio/")
async def upload_audio_file(file: Annotated[UploadFile, File()]):
    """
    Receives an audio file, validates its type, and saves it to the server.
    Supported formats: .mp3, .m4a, .wav
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only .mp3, .m4a, and .wav are supported. Found: {file.content_type}"
        )

    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    #Return a success response
    return {
        "message": f"File '{file.filename}' uploaded successfully.",
        "saved_path": file_path,
        "content_type": file.content_type
    }