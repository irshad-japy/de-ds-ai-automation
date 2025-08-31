# src/tts/xtts_tts.py
from __future__ import annotations
from pathlib import Path
from typing import Optional
import torch
from TTS.api import TTS

class XTTS:
    """
    Open-source TTS using Coqui XTTS-v2 (multilingual, zero-shot voice cloning).
    """
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2", device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tts = TTS(model_name).to(self.device)

    def tts(
        self,
        text: str,
        out_path: Path,
        speaker_wav: Optional[Path] = None,
        language: str = "en",
        speed: float = 1.0,
    ) -> Path:
        """
        If speaker_wav is provided, XTTS will mimic the voice (zero-shot cloning).
        """
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        self.tts.tts_to_file(
            text=text,
            speaker_wav=str(speaker_wav) if speaker_wav else None,
            language=language,
            file_path=str(out_path),
            speed=speed,
        )
        return out_path
