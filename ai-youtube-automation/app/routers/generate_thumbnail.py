from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import logging, time, os
from app.services.generate_thumbnail import generate_thumbnail_from_script, logger
from app.utils.resource_monitor import resource_monitor
import asyncio
HEAVY_JOB_SEM = asyncio.Semaphore(1)
from app.utils.subprocess_runner import run_worker, SubprocessError

router = APIRouter(prefix="/thumbnail", tags=["generate"])

class ThumbnailRequest(BaseModel):
    script: str = Field(..., min_length=10, description="Full video script text")
    seed: int = Field(42, ge=0, le=2_147_483_647, description="Seed for deterministic output")

@router.post("/generate-thumbnail")
@resource_monitor(
    logger,
    include_gpu=True,
    slow_ms_threshold=2000,  # log only if >=2s
    sample_rate=1,
    tag="thumbnail",
)
async def generate_thumbnail_api(payload: ThumbnailRequest):
    """
    Accepts script text in JSON and returns a PNG thumbnail.
    Body:
    {
      "script": "Title: ...\\nScene 1: ...",
      "seed": 42
    }
    """
    # async with HEAVY_JOB_SEM:
    try:
        start = time.time()
        logger.info(f'payload: {payload}')
        # out_path: Path = generate_thumbnail_from_script(payload.script, seed=payload.seed)

        worker_payload = payload.model_dump()

        result_raw = run_worker("app.workers.thumbnail_worker", worker_payload)

        lines = [ln.strip() for ln in str(result_raw).splitlines() if ln.strip()]
        result_path = lines[-1]

        if not os.path.exists(result_path):
            raise HTTPException(status_code=500, detail="Thumbnail generation failed (file not found).")
        logger.info(f'out_path: {result_path}')
        end = time.time()
        logger.info(f'total time to generate thumbnail: {end - start:.2f} second')

        full_path = Path(result_path).resolve().as_posix()
        return full_path

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
