# scripts/generate_voice.py
"""
python app/services/generate_voice.py
python -m app.services.generate_voice
"""

import os
import requests
from app.utils.config import settings
from pathlib import Path
from typing import Optional

def _ensure_parent_dir(path: Path) -> None:
    """Create parent directory for the given file path if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)

def generate_voice(text: str, speaker_id: str, out_path: str | Path, language: Optional[str] = 'en'):
    """Generate voice using ElevenLabs API for any text-based file."""

    out_path = Path(out_path).expanduser()
    # If out_path is relative, place it under OUTPUT_ROOT
    if not out_path.is_absolute():
        out_path = 'output' / out_path
    _ensure_parent_dir(out_path)

    if not text.strip():
        raise ValueError("Input file is empty!")

    # api_key = settings("ELEVENLABS_API_KEY")
    api_key = "sk_bcdb849f7a903076c4fb58d06a7cce041dd170154c4373f1"
    if not api_key:
        raise EnvironmentError("Missing ELEVEN_LABS_API key in settings")

      # Default voice
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{speaker_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"API Error {response.status_code}: {response.text}")

    with open(out_path, "wb") as out:
        out.write(response.content)

    print(f"✅ Voice generated: {out_path}")
    return out_path

# ---------------------------------------------------------------
if __name__ == "__main__":
    text = 'This is our second episode on Vande Mataram. In this episode, we talk about Anandamath and Mahatma Gandhi’s views. This video is also a bit long. After this, there will be a third video as well, based on the debate that took place in the Lok Sabha today. Stay tuned for that too.'
    speaker_id = "TX3LPaxmHKxFdv7VOQHJ"
    out_path = 'clone_voice/elevanlabs_1.mp3'
    language = 'en'
    generate_voice(text, speaker_id, out_path, language)