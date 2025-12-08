from pathlib import Path
from typing import Optional
import base64
import mimetypes

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/read_script", tags=["YouTube Uploader API"])

class ScriptPathRequest(BaseModel):
    script_file_path: str            # full path to .txt script
    video_file_path: Optional[str]   # full path to video (mp4, etc.)

class ScriptResponse(BaseModel):
    script_file_path: str
    video_file_path: Optional[str] = None
    script_text: str

    # video info
    video_file_name: Optional[str] = None
    video_mime_type: Optional[str] = None
    video_base64: Optional[str] = None   # <== full video data here

@router.post("/read-from-path", response_model=ScriptResponse)
async def read_from_path(body: ScriptPathRequest):
    """
    Take script file path + video file path from user.
    - Read script as text
    - Read video as bytes and return base64 string
    """
    # --- script part ---
    script_path = Path(body.script_file_path).expanduser()

    if not script_path.exists() or not script_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Script file not found: {script_path}",
        )

    try:
        script_text = script_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading script file: {e}",
        )

    # --- video part (optional) ---
    video_file_name = None
    video_mime_type = None
    video_base64 = None

    if body.video_file_path:
        video_path = Path(body.video_file_path).expanduser()

        if not video_path.exists() or not video_path.is_file():
            raise HTTPException(
                status_code=404,
                detail=f"Video file not found: {video_path}",
            )

        try:
            video_bytes = video_path.read_bytes()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading video file: {e}",
            )

        # encode to base64 for JSON
        video_base64 = base64.b64encode(video_bytes).decode("ascii")
        video_file_name = video_path.name
        video_mime_type = mimetypes.guess_type(str(video_path))[0] or "video/mp4"

    return ScriptResponse(
        script_file_path=str(script_path),
        video_file_path=body.video_file_path,
        script_text=script_text,
        video_file_name=video_file_name,
        video_mime_type=video_mime_type,
        video_base64=video_base64,
    )
