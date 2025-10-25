# ai_youtube_video_bot/api/main.py
from fastapi import FastAPI, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import FileResponse
import tempfile, os

# from ..services.generate_voice import generate_voice
from ..services.generate_voice_2 import generate_voice

# app = FastAPI(title="Voice Generator API")
router = APIRouter(prefix="/generate_voice", tags=["generate"])

@router.post("/generate-voice")
async def generate_voice_api(file: UploadFile, filename: str = Form(None)):
    """
    Accept any text-based file (.py, .txt, .json, etc.) and return an MP3 voice file.
    """
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename or "input.txt")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="wb") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        output_path = f"output/{os.path.splitext(file.filename)[0]}.mp3"
        path = generate_voice(script_path=tmp_path, output_path=output_path)

        return FileResponse(path, media_type="audio/mpeg", filename=os.path.basename(path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
