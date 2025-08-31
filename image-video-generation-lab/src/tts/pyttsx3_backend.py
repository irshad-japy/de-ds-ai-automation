from __future__ import annotations
from pathlib import Path
import pyttsx3

def pyttsx3_synth(text: str, out_path: Path, rate: int = 175, voice: str | None = None) -> Path:
    out_path = Path(out_path).with_suffix(".wav")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    eng = pyttsx3.init()
    if voice:
        for v in eng.getProperty("voices"):
            if voice.lower() in (v.name or "").lower():
                eng.setProperty("voice", v.id); break
    eng.setProperty("rate", rate)
    eng.save_to_file(text, str(out_path))
    eng.runAndWait()
    return out_path
