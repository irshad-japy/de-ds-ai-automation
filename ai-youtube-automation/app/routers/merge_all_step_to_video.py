from pathlib import Path
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from app.services.merge_all_step_to_video import merge_main

router = APIRouter(prefix="/merge_video", tags=["video-merge"])

class MergeRequest(BaseModel):
    full_video_path: str = Field(..., description="Main video path (mp4)")
    full_audio_path: str = Field(..., description="Main voice audio path (wav/mp3)")
    cut_mode: str = Field("none", description="none | cut_video | cut_audio")
    hook_audio: str
    hook_video: str
    thumbnail_path: str
    music_path: str

@router.post("/merge_all_step", response_class=FileResponse)
def merge_all_step_video(req: MergeRequest):
    full_video_path = Path(req.full_video_path)
    full_audio_path = Path(req.full_audio_path)
    hook_audio = Path(req.hook_audio)
    hook_video = Path(req.hook_video)
    thumbnail_path = Path(req.thumbnail_path)
    music_path = Path(req.music_path)

    # Validate inputs
    for p, label in [
        (full_video_path, "full_video_path"),
        (full_audio_path, "full_audio_path"),
        (hook_audio, "hook_audio"),
        (hook_video, "hook_video"),
        (thumbnail_path, "thumbnail_path"),
        (music_path, "music_path"),
    ]:
        if not p.exists():
            raise HTTPException(status_code=400, detail=f"{label} not found: {p}")
        if not p.is_file():
            raise HTTPException(status_code=400, detail=f"{label} is not a file: {p}")
    try:
        out_path = merge_main(
            full_video_path=full_video_path,
            full_audio_path=full_audio_path,
            cut_mode=req.cut_mode,
            hook_audio=hook_audio,
            hook_video=hook_video,
            thumbnail_path=thumbnail_path,
            music_path=music_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {e}")

    out_path = Path(out_path)
    if not out_path.exists():
        raise HTTPException(status_code=500, detail=f"Output file not created: {out_path}")

    return FileResponse(
        path=str(out_path),
        media_type="video/mp4",
        filename=os.path.basename(str(out_path)),
    )
