# ai_youtube_video_bot/api/main.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal, Optional
from pathlib import Path
import os, gc, logging
from datetime import datetime

from app.services.xtts_voice_helper import logger
from app.utils.resource_monitor import resource_monitor

import asyncio
HEAVY_JOB_SEM = asyncio.Semaphore(1)
from app.utils.subprocess_runner import run_worker, SubprocessError

router = APIRouter(prefix="/generate_voice", tags=["generate"])

# ---------- Request body model ----------

class VoiceRequest(BaseModel):
    text: str
    service_model: Literal["TTS", "ElevenLabs", "Default"] = "Default"
    speaker_id: Optional[str] = None
    language: str = "en"

# ---------- Endpoint ----------
@router.post("/generate-voice")
@resource_monitor(
    logger,
    include_gpu=True,
    slow_ms_threshold=0,  # set 0 while testing
    sample_rate=1,
    tag="text_to_voice",
)
async def generate_voice_api(payload: VoiceRequest):
    """
    Generate voice for given text using XTTS (TTS), ElevenLabs or default system voice.

    - `language` is optional (default: "en")
    - `out_path` is optional (default: auto file name under ./outputs)
    - `service_model` "TTS", "ElevenLabs", "Default"
    """
    # async with HEAVY_JOB_SEM:
    try:
        project_root = Path(__file__).resolve().parents[2]
        output_dir = project_root / "output" / "clone_voice"
        output_dir.mkdir(parents=True, exist_ok=True)

        ext = ".wav"

        # ✅ unique suffix: YYYYMMDD_HHMMSS_microseconds
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        out_filename = f"{payload.service_model.lower()}_voice_{ts}{ext}"
        out_path = output_dir / out_filename

        worker_payload = payload.model_dump()
        worker_payload["out_path"] = str(out_path)

        result_raw = run_worker("app.workers.voice_worker", worker_payload)

        lines = [ln.strip() for ln in str(result_raw).splitlines() if ln.strip()]
        result_path = lines[-1]

        # ---------- Validate file & return ----------
        if not os.path.exists(result_path):
            raise HTTPException(
                status_code=500,
                detail=f"Voice file not found at path: {result_path}",
            )

        # ✅ Convert to absolute/full path
        full_path = Path(result_path).resolve().as_posix()

        # ✅ Return only output_path with full location
        return full_path
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating voice: {e}")
    