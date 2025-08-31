from __future__ import annotations
from pathlib import Path
import asyncio, edge_tts

async def _edge_tts_async(text: str, voice: str, rate: str, volume: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume)
    await communicate.save(str(out_path))

def edge_tts_synth(text: str, out_path: Path, voice: str = "en-US-AriaNeural", rate: str = "+0%", volume: str = "+0dB") -> Path:
    asyncio.run(_edge_tts_async(text, voice, rate, volume, Path(out_path)))
    return Path(out_path)
