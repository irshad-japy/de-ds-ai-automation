from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests, time

ELEVEN_BASE = "https://api.elevenlabs.io/v1"

class ElevenLabsTTS:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY is required.")
        self.api_key = api_key

    def _headers(self, accept: str = "application/json") -> Dict[str, str]:
        return {"xi-api-key": self.api_key, "accept": accept}

    def synth(
        self,
        text: str,
        out_path: Path,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        voice_settings: Optional[Dict[str, Any]] = None,
        audio_format: str = "mp3",
    ) -> Path:
        out_path = Path(out_path).with_suffix("." + audio_format)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"{ELEVEN_BASE}/text-to-speech/{voice_id}"
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings or {"stability": 0.5, "similarity_boost": 0.5},
        }
        headers = {"xi-api-key": self.api_key, "accept": f"audio/{audio_format}", "Content-Type": "application/json"}
        r = requests.post(url, headers=headers, json=payload, timeout=300)
        r.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r.content)
        return out_path

    def create_voice_from_audio(self, name: str, audio_files: List[Path]) -> str:
        url = f"{ELEVEN_BASE}/voices/add"
        files = [("files", (Path(p).name, open(p, "rb"), "audio/mpeg")) for p in audio_files]
        data = {"name": name}
        r = requests.post(url, headers=self._headers(), data=data, files=files, timeout=300)
        r.raise_for_status()
        js = r.json()
        vid = js.get("voice_id") or js.get("voice", {}).get("voice_id")
        if not vid:
            raise RuntimeError(f"Unable to parse voice_id: {js}")
        return vid

    def clone_and_synth(
        self,
        text: str,
        out_path: Path,
        ref_audio: List[Path],
        new_voice_name: str = "MyClonedVoice",
        model_id: str = "eleven_multilingual_v2",
        audio_format: str = "mp3",
    ) -> Path:
        voice_id = self.create_voice_from_audio(new_voice_name, ref_audio)
        time.sleep(2.0)  # small delay to ensure availability
        return self.synth(text, out_path, voice_id=voice_id, model_id=model_id, audio_format=audio_format)
