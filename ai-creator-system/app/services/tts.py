from pathlib import Path
import pyttsx3
from ..utils.logging import logger

def tts_offline(text: str, out_path: Path) -> Path:
    """
    Generate offline TTS audio and save to the given path.
    Ensures that the parent directory exists before saving.
    Compatible with orchestration pipeline and FastAPI endpoints.
    """
    # ✅ Convert to Path if passed as string
    out_path = Path(out_path)

    # ✅ Ensure the directory exists before writing
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ Initialize offline TTS engine
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    # ✅ Generate the MP3 file
    engine.save_to_file(text, str(out_path))
    engine.runAndWait()

    logger.info(f"✅ Saved narration TTS to {out_path}")
    return out_path
