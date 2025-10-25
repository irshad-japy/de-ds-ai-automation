"""
Offline universal voice generator (no ElevenLabs)
Supports: .txt, .py, .json, .csv, .dockerfile, .pdf, etc.
Output: .mp3 (offline TTS)
"""

import os
import json
import pyttsx3
from PyPDF2 import PdfReader

# ===================================================
# ✅ Function to extract text from different file types
# ===================================================
def extract_text_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext in [".txt", ".py", ".json", ".csv", ".log", ".yml", ".yaml", ".dockerfile", ""]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        elif ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""

        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        if not text.strip():
            raise ValueError("No readable text found in the file.")
        return text

    except Exception as e:
        raise RuntimeError(f"Error extracting text: {e}")

# ===================================================
# ✅ Generate voice using pyttsx3 (offline)
# ===================================================
def generate_voice(script_path: str, output_path: str = "output/voice_output.mp3"):
    # Extract text
    text = extract_text_from_file(script_path)

    # Create output directory if missing
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Initialize pyttsx3 engine
    engine = pyttsx3.init()

    # Optional: voice settings
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)      # change [0] to [1] for female voice if available
    engine.setProperty('rate', 175)                # speed
    engine.setProperty('volume', 1.0)              # 0.0 to 1.0

    print("🎙️ Generating offline voice...")
    engine.save_to_file(text, output_path)
    engine.runAndWait()

    print(f"✅ Voice generated: {output_path}")
    return output_path

# ===================================================
# ✅ Run directly from CLI
# ===================================================
if __name__ == "__main__":
    # Example usage
    input_file = r"ai_youtube_video_bot/output/alarm_clock_story.txt"  # Change to your file path
    output_file = r"ai_youtube_video_bot/output/voice_offline.mp3"
    generate_voice(input_file, output_file)
