"""
FastAPI endpoint to explain uploaded files as stories/scripts and generate voice narration.
Accepts file upload via form-data.
"""

from fastapi import FastAPI, UploadFile, HTTPException, APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import requests, io, os, pathlib, tempfile, time, base64
from gtts import gTTS
from pydub import AudioSegment
from PyPDF2 import PdfReader

# ---------- CONFIG ----------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b-instruct-q4_K_M")
OUTPUT_DIR = pathlib.Path("output").resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 2 * 1024 * 1024  # 2MB limit

# ---------- HELPERS ----------
def extract_text(file_path: str) -> str:
    """Read text from txt/py/json/pdf files."""
    ext = pathlib.Path(file_path).suffix.lower()
    text = ""
    if ext in [".txt", ".py", ".json", ".csv", ".log"]:
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

def build_prompt(source_code: str, mode: str = "story") -> str:
    """Build structured prompt for Ollama."""
    return f"""
You are a senior engineer and storyteller.
Explain the uploaded file as a {mode}.
Keep it vivid but technically precise.

Structure:
1) Hook
2) Cast (main functions/classes)
3) Plot (goal of the script)
4) Scenes (step-by-step explanation)
5) Twist (edge cases or errors)
6) Moral (key takeaways)
7) Quiz (3 MCQs with answers)

CODE:
{source_code[:3000]}  # truncated if too large
""".strip()

def call_ollama_generate(prompt: str) -> str:
    """Send prompt to Ollama and return response."""
    try:
        r = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        story = (data.get("response") or "").strip()
        if not story:
            raise ValueError("Empty response from Ollama.")
        return story
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama request failed: {e}")

def tts_gtts(text: str, lang: str = "en") -> bytes:
    """Convert text to speech (MP3) using gTTS."""
    try:
        tts = gTTS(text=text, lang=lang)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

def mix_bgm(narration_bytes: bytes, bg_music_path: Optional[str]) -> bytes:
    """Mix background music with narration."""
    if not bg_music_path or not os.path.exists(bg_music_path):
        return narration_bytes

    narr = AudioSegment.from_file(io.BytesIO(narration_bytes), format="mp3")
    bg = AudioSegment.from_file(bg_music_path)

    if len(bg) < len(narr):
        bg *= (len(narr) // len(bg)) + 1
    bg = bg[:len(narr)]

    mixed = bg - 22
    narr = narr - 2
    final = mixed.overlay(narr)

    out_buf = io.BytesIO()
    final.export(out_buf, format="mp3")
    return out_buf.getvalue()

# ---------- FASTAPI ----------
router = APIRouter(prefix="/generate", tags=["generate"])

@router.post("/explain-file")
async def explain_file(file: UploadFile, mode: str = "story", lang: str = "en", bg_music_path: Optional[str] = None):
    """
    Upload any text/code/pdf file to get:
    1️⃣ Story/script explanation from Ollama
    2️⃣ MP3 voice narration (via gTTS)
    """
    try:
        # Save uploaded file
        suffix = os.path.splitext(file.filename or "input.txt")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="wb") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 1. Extract text
        text = extract_text(tmp_path)

        # 2. Build and send prompt
        prompt = build_prompt(text, mode)
        story = call_ollama_generate(prompt)

        # 3. Generate TTS
        audio_bytes = tts_gtts(story, lang=lang)

        # 4. Optional background mix
        audio_bytes = mix_bgm(audio_bytes, bg_music_path)

        # 5. Save to disk
        safe_name = pathlib.Path(file.filename).stem or "file"
        ts = time.strftime("%Y%m%d_%H%M%S")
        mp3_path = OUTPUT_DIR / f"{safe_name}_{ts}.mp3"
        mp3_path.write_bytes(audio_bytes)

        # Return both text + downloadable file
        return {
            "meta": {
                "file": file.filename,
                "mode": mode,
                "language": lang,
                "saved_to": str(mp3_path)
            },
            "story": story,
            "audio_b64": base64.b64encode(audio_bytes).decode("utf-8")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
