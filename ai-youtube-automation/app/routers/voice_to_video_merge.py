# app/api/routes/video_merge.py

from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from app.services.voice_to_video_merge import merge_voice_and_video

router = APIRouter(prefix="/video", tags=["video-merge"])

class MergeRequest(BaseModel):
    video_path: str
    audio_path: str

class MergeResponse(BaseModel):
    output_path: str
    size_bytes: int

@router.post("/merge", response_model=MergeResponse)
def merge_video_and_audio(req: MergeRequest):
    video_path = Path(req.video_path)
    audio_path = Path(req.audio_path)

    if not video_path.exists():
        raise HTTPException(status_code=400, detail=f"Video not found: {video_path}")
    if not audio_path.exists():
        raise HTTPException(status_code=400, detail=f"Audio not found: {audio_path}")

    try:
        out_path = merge_voice_and_video(video_path, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {e}")

    return FileResponse(
        out_path,
        media_type='video/mp4',
        filename=os.path.basename(out_path),
    )
