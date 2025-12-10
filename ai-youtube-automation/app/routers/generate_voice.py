# ai_youtube_video_bot/api/main.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal, Optional
from pathlib import Path
import os

from ..services.generate_voice import generate_voice as eleven_generate_voice
from ..services.generate_voice_2 import generate_voice as default_generate_system_voice
from ..services.xtts_voice_helper import tts_with_cached_speaker

router = APIRouter(prefix="/generate_voice", tags=["generate"])

# ---------- Request body model ----------

class VoiceRequest(BaseModel):
    text: str
    # which engine to use
    service_model: Literal["TTS", "ElevenLabs", "Default"] = "Default"
    # speaker_id is optional overall, but required for some engines
    speaker_id: Optional[str] = None
    # language optional, default English
    language: str = "en"
    # optional full or relative path; if None, we auto-generate
    out_path: Optional[str] = None

# ---------- Endpoint ----------

@router.post("/generate-voice")
async def generate_voice_api(payload: VoiceRequest):
    """
    Generate voice for given text using XTTS (TTS), ElevenLabs or default system voice.

    - `language` is optional (default: "en")
    - `out_path` is optional (default: auto file name under ./outputs)
    - `service_model` "TTS", "ElevenLabs", "Default"
    """

    try:
        # Ensure output directory
        base_dir = Path("clone_voice")
        base_dir.mkdir(exist_ok=True)

        # Decide output file path
        if payload.out_path:
            out_path = Path(payload.out_path)
            # if a bare filename is passed, save it under outputs/
            if not out_path.is_absolute():
                out_path = base_dir / out_path
        else:
            # simple default name based on service_model
            ext = ".wav"
            out_path = base_dir / f"{payload.service_model.lower()}_voice{ext}"

        # Make sure parent folder exists
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # ---------- Select engine ----------
        if payload.service_model == "TTS":
            # XTTS typically needs a speaker_id
            if not payload.speaker_id:
                raise HTTPException(
                    status_code=400,
                    detail="speaker_id is required when service_model='TTS'",
                )
            path = tts_with_cached_speaker(
                text=payload.text,
                speaker_id=payload.speaker_id,
                out_path=str(out_path),
                language=payload.language,
            )

        elif payload.service_model == "ElevenLabs":
            if not payload.speaker_id:
                raise HTTPException(
                    status_code=400,
                    detail="speaker_id is required when service_model='ElevenLabs'",
                )
            path = eleven_generate_voice(
                text=payload.text,
                speaker_id=payload.speaker_id,
                out_path=str(out_path),
                language=payload.language,
            )

        else:  # "Default"
            path = default_generate_system_voice(
                text=payload.text,
                out_path=str(out_path),
            )

        # ---------- Validate file & return ----------
        if not os.path.exists(path):
            raise HTTPException(
                status_code=500,
                detail=f"Voice file not found at path: {path}",
            )

        # media type based on extension
        if str(path).lower().endswith(".mp3"):
            media_type = "audio/mpeg"
        else:
            media_type = "audio/wav"

        return FileResponse(
            path,
            media_type=media_type,
            filename=os.path.basename(path),
        )

    except HTTPException:
        # re-raise our own HTTP errors
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating voice: {e}")
