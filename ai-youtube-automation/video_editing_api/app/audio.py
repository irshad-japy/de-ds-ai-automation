
from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Optional
from .utils import require_ffmpeg

def denoise_and_normalize(in_video: Path, out_video: Path, use_rnnoise: bool=False) -> None:
    ff = require_ffmpeg()
    af = "highpass=f=80,lowpass=f=12000,afftdn=nr=12:nt=w,loudnorm=I=-16:LRA=11:TP=-1.5"
    cmd = [
        ff, "-y", "-i", str(in_video),
        "-map", "0:v:0", "-c:v", "copy",
        "-map", "0:a:0", "-c:a", "aac", "-b:a", "192k",
        "-af", af,
        str(out_video)
    ]
    subprocess.run(cmd, check=True)

def ffmpeg_replace_audio(video: Path, audio_wav: Path, out_video: Path, loudnorm: bool=True):
    ff = require_ffmpeg()
    af = "loudnorm=I=-16:LRA=11:TP=-1.5" if loudnorm else "anull"
    cmd = [
        ff, "-y",
        "-i", str(video),
        "-i", str(audio_wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", af, "-shortest",
        str(out_video)
    ]
    subprocess.run(cmd, check=True)

def estimate_rate_for_duration(words: int, target_seconds: int, default_rate: int = 180) -> int:
    target_wpm = max(110, min(200, int((words / max(1,target_seconds)) * 60)))
    return int(default_rate * (target_wpm / 160.0))

def tts_synthesize_to_wav(text: str, out_wav: Path, voice_id: Optional[str]=None, rate: Optional[int]=None, volume: float = 1.0):
    import pyttsx3
    engine = pyttsx3.init()
    if voice_id:
        try:
            engine.setProperty("voice", voice_id)
        except Exception:
            pass
    if rate:
        engine.setProperty("rate", int(rate))
    engine.setProperty("volume", float(volume))
    engine.save_to_file(text, str(out_wav))
    engine.runAndWait()
