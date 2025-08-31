# src/tts/elevenlabs_tts.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
import json
import time

ELEVEN_BASE = "https://api.elevenlabs.io/v1"

class ElevenLabsTTS:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY is required for ElevenLabs backend.")
        self.api_key = api_key
        self.headers = {
            "xi-api-key": self.api_key,
        }

    def synth(
        self,
        text: str,
        out_path: Path,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: Optional[Dict[str, Any]] = None,
        format: str = "mp3",
    ) -> Path:
        """
        Generate speech to out_path using an existing voice_id.
        """
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"{ELEVEN_BASE}/text-to-speech/{voice_id}"
        headers = {
            **self.headers,
            "accept": f"audio/{format}",
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings or {"stability": 0.5, "similarity_boost": 0.5},
        }
        r = requests.post(url, headers=headers, json=payload, timeout=300)
        r.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r.content)
        return out_path

    def create_voice_from_audio(self, name: str, audio_files: List[Path]) -> str:
        """
        Create a new ElevenLabs voice by uploading 1..N reference audio files.
        Returns the new voice_id.
        """
        url = f"{ELEVEN_BASE}/voices/add"
        files = []
        for af in audio_files:
            files.append(("files", (Path(af).name, open(af, "rb"), "audio/mpeg")))
        data = {"name": name}
        headers = {**self.headers}
        r = requests.post(url, headers=headers, data=data, files=files, timeout=300)
        r.raise_for_status()
        js = r.json()
        voice_id = js.get("voice_id") or js.get("voice", {}).get("voice_id")
        if not voice_id:
            raise RuntimeError(f"Could not parse new voice_id from response: {js}")
        return voice_id

    def clone_and_synth(
        self,
        text: str,
        out_path: Path,
        ref_audio: List[Path],
        new_voice_name: str = "MyClonedVoice",
        model_id: str = "eleven_multilingual_v2",
        format: str = "mp3",
    ) -> Path:
        """
        Upload reference audio to create a new voice, then synthesize speech with it.
        """
        voice_id = self.create_voice_from_audio(new_voice_name, ref_audio)
        # small delay to allow indexing (often not required, but safe)
        time.sleep(2.0)
        return self.synth(text, out_path, voice_id=voice_id, model_id=model_id, format=format)
