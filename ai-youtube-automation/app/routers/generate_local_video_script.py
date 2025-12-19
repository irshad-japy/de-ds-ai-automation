from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
import re
from app.services.generate_local_video_script import extract_audio_from_video, transcribe_audio, save_transcript

router = APIRouter(prefix="/script", tags=["local_video"])

@router.post("/local_extract_script")
async def local_extract_script(
    file: UploadFile = File(...),
    model_name: str = Form("base")
):
    """
    Upload a local video file, extract its audio,
    transcribe speech to text, deduplicate, and save transcript.
    """
    try:
        # Step 1️⃣: Save uploaded video locally
        os.makedirs("temp_videos", exist_ok=True)
        video_path = os.path.join("temp_videos", file.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📂 Video saved locally: {video_path}")

        # Step 2️⃣: Extract audio and transcribe
        audio_path = extract_audio_from_video(video_path)
        segments = transcribe_audio(audio_path, model_name)
        saved_path = save_transcript(segments, file.filename)

        return {
            "file_name": file.filename,
            "model_used": model_name,
            "saved_transcript": saved_path,
            "message": "Transcript generated and saved successfully!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # optional cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists("temp_videos") and not os.listdir("temp_videos"):
            os.rmdir("temp_videos")