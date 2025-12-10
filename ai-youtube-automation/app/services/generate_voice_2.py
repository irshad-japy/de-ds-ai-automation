"""
python app/services/generate_voice_2.py
python -m app.services.generate_voice

Offline universal voice generator (no ElevenLabs)
Supports: .txt, .py, .json, .csv, .dockerfile, .pdf, etc.
Output: .wav (offline TTS)
"""

import os
import pyttsx3
from pathlib import Path
from typing import Optional

def _ensure_parent_dir(path: Path) -> None:
    """Create parent directory for the given file path if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)

# ===================================================
# ✅ Generate voice using pyttsx3 (offline)
# ===================================================
def generate_voice(text: str, out_path: str = "clone_voice/voice_output.wav"):
    # Extract text
    # text = extract_text_from_file(script_path)
    out_path = Path(out_path).expanduser()

    # If out_path is relative, place it under OUTPUT_ROOT
    if not out_path.is_absolute():
        out_path = Path("output") / out_path

    _ensure_parent_dir(out_path)

    # Create output directory if missing (redundant safety – same logic)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Initialize pyttsx3 engine
    engine = pyttsx3.init()

    # Optional: voice settings
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)      # change [0] to [1] for female voice if available
    engine.setProperty('rate', 175)                # speed
    engine.setProperty('volume', 1.0)              # 0.0 to 1.0

    print("🎙️ Generating offline voice...")
    engine.save_to_file(text, str(out_path))
    engine.runAndWait()

    resolved = out_path.resolve()
    print(f"✅ Voice generated: {resolved}")
    return resolved

# ===================================================
# ✅ Run directly from CLI
# ===================================================
if __name__ == "__main__":
    # Example usage
    input_text = "This is a sample offline TTS generated using pyttsx3."
    output_file = "clone_voice/voice_output_1.wav"
    generate_voice(input_text, output_file)
