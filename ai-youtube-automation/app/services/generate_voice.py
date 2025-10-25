# scripts/generate_voice.py
import os
import requests
from utils.config import settings

def generate_voice(script_path: str, output_path: str = "output/voice.mp3"):
    """Generate voice using ElevenLabs API for any text-based file."""

    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script file not found: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        raise ValueError("Input file is empty!")

    api_key = settings.get("ELEVEN_LABS_API")
    if not api_key:
        raise EnvironmentError("Missing ELEVEN_LABS_API key in settings")

    voice_id = "Xb7hH8MSUJpSbSDYk0k2"  # Default voice
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

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

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as out:
        out.write(response.content)

    print(f"✅ Voice generated: {output_path}")
    return output_path
