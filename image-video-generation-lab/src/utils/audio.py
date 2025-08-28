import os, io, tempfile
from pathlib import Path
from typing import Optional
import pyttsx3

def tts_offline_to_wav(text: str, out_path: Path) -> Path:
    """Synthesize speech offline using pyttsx3 to WAV."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    engine.save_to_file(text, str(out_path))
    engine.runAndWait()
    return out_path

def tts_elevenlabs_to_wav(text: str, api_key: str, voice: str, out_path: Path) -> Path:
    import requests
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice
    headers = {"xi-api-key": api_key, "accept": "audio/mpeg", "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    mp3_path = out_path.with_suffix(".mp3")
    with open(mp3_path, "wb") as f: f.write(r.content)

    # Convert MP3 -> WAV using moviepy (ffmpeg)
    from moviepy import AudioFileClip
    clip = AudioFileClip(str(mp3_path))
    clip.write_audiofile(str(out_path), fps=44100, nbytes=2, codec="pcm_s16le", verbose=False, logger=None)
    clip.close()
    return out_path
