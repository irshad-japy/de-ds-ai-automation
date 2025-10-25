# app.py — single-file FastAPI service (robust + saves MP3s to ./output)
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, field_validator
from typing import Optional, Tuple
import requests, base64, os, pathlib, io, tempfile, time
from gtts import gTTS
from pydub import AudioSegment

# ---- Config ----
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")   # e.g. http://localhost:11434
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")               # e.g. llama3.1, qwen2.5:14b, etc.
MAX_BYTES    = 2 * 1024 * 1024                                     # 2 MB cap to avoid huge/binary blobs
OUTPUT_DIR   = pathlib.Path(os.getenv("OUTPUT_DIR", "./output")).expanduser()

# Ensure output folder exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Schemas ----
class ExplainControls(BaseModel):
    target_audience: str = "Beginner"
    tone: str = "calm"                 # calm | witty | adventurous ...
    humor_level: int = 1               # 0..3
    reading_time_sec: int = 90
    target_words: int = 180
    analogy_domain: Optional[str] = None
    language: str = "English"          # prose language name used in prompt

class ExplainRequest(BaseModel):
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    mode: str = "story"                # "story" or "script"
    language: str = "en"               # gTTS language code (e.g., "en", "hi")
    bg_music_path: Optional[str] = None
    controls: ExplainControls = ExplainControls()

    @field_validator("mode")
    @classmethod
    def _check_mode(cls, v: str) -> str:
        if v not in {"story", "script"}:
            raise ValueError("mode must be 'story' or 'script'")
        return v

# ---- Small helpers for errors ----
def _http_400(msg: str) -> HTTPException: return HTTPException(status_code=400, detail=msg)
def _http_413(msg: str) -> HTTPException: return HTTPException(status_code=413, detail=msg)
def _http_502(msg: str) -> HTTPException: return HTTPException(status_code=502, detail=msg)

# ---- Core helpers ----
def load_source(*, file_url: Optional[str], file_path: Optional[str]) -> Tuple[str, str]:
    """
    Return (source_text, source_name). Exactly one of file_url/file_path must be provided.
    """
    # XOR check: True if exactly one of them is provided
    if (file_url is None and file_path is None) or (file_url and file_path):
        raise _http_400("Provide exactly one of file_url or file_path.")

    if file_url:
        try:
            r = requests.get(file_url, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            raise _http_400(f"Failed to download file_url: {e}")
        data = r.content
        if len(data) > MAX_BYTES:
            raise _http_413(f"Source too large (> {MAX_BYTES} bytes).")
        text = data.decode("utf-8", errors="replace")
        name = file_url.split("/")[-1] or "remote_file"
        return text, name

    # Local file branch
    p = pathlib.Path(file_path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise _http_400(f"file_path not found: {p}")
    data = p.read_bytes()
    if len(data) > MAX_BYTES:
        raise _http_413(f"Source too large (> {MAX_BYTES} bytes).")
    text = data.decode("utf-8", errors="replace")
    return text, p.name

def build_prompt(*, source_code: str, controls: ExplainControls, mode: str) -> str:
    """
    Structured prompt per your spec. Works for any text/code file.
    """
    prose_language = controls.language
    return f"""
You are a friendly senior engineer + storyteller.
Audience: {controls.target_audience} (beginner/intermediate/advanced).
Goal: Explain the file below as a short story without losing correctness.

Rules:
- Keep it vivid, but precise. No hallucinations.
- Prefer present tense. Second person (“you”) POV.
- Use clear scene beats and understatement; no purple prose.
- Mention function/class names exactly once when introduced.
- If code uses external APIs or files, state that explicitly.

Structure (use these headings):
1) Hook (1–2 lines)
2) Cast (key functions/classes as characters)
3) Plot (what problem the code solves)
4) Scenes (step-by-step execution as story beats)
5) Twist (edge cases, errors, or performance traps)
6) Moral (3–5 bullet key takeaways)
7) Quiz (3 questions, each with A/B/C, and the answer key)

Voice & Style Controls:
- Tone: {controls.tone}
- Humor level: {controls.humor_level}/3
- Reading time target: {controls.reading_time_sec} seconds ≈ {controls.target_words} words.
- Analogy domain (optional): {controls.analogy_domain or "none"}
- Language: {prose_language}

When helpful for audio, include subtle stage cues in [brackets] like:
[footsteps fade in], [pause], [keyboard clack].

CODE:

Respond only with the {'story' if mode == 'story' else 'script'} in the specified structure and language.
If the file is not Python, still explain the logic faithfully and precisely.
""".strip()

def call_ollama_generate(*, model: str, prompt: str) -> str:
    url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        r = requests.post(url, json=payload, timeout=180)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise _http_502(f"Ollama request failed: {e}")
    except ValueError:
        raise _http_502("Invalid JSON from Ollama.")
    text = (data.get("response") or "").strip()
    if not text:
        raise _http_502("Empty response from Ollama.")
    return text

def tts_gtts(text: str, lang: str = "en") -> bytes:
    """
    gTTS entirely in-memory to avoid Windows temp-file locks (WinError 32).
    """
    try:
        tts = gTTS(text=text, lang=lang)
        buf = io.BytesIO()
        tts.write_to_fp(buf)  # write MP3 bytes directly to memory
        return buf.getvalue()
    except Exception as e:
        raise _http_502(f"gTTS synthesis failed: {e}")

def mix_bgm(narration_mp3: bytes, bg_path: str, narration_db: float = -1.5, bg_db: float = -22.0) -> bytes:
    """
    Mix a background track with the narration MP3 (requires ffmpeg for pydub).
    """
    try:
        narr = AudioSegment.from_file(io.BytesIO(narration_mp3), format="mp3")
    except Exception as e:
        raise _http_502(f"Failed to parse narration MP3: {e}")

    p = pathlib.Path(bg_path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise _http_400(f"bg_music_path not found: {p}")

    try:
        bg = AudioSegment.from_file(str(p))
    except Exception as e:
        raise _http_502(f"Failed to read bg_music_path: {e}")

    # Loop bg to cover narration if needed
    if len(bg) < len(narr):
        loops = len(narr) // len(bg) + 1
        bg = bg * loops
    bg = bg[:len(narr)]
    narr = narr + narration_db
    bg = bg + bg_db

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        out_path = tmp.name
    mixed = bg.overlay(narr)
    mixed.export(out_path, format="mp3")
    try:
        return pathlib.Path(out_path).read_bytes()
    finally:
        try:
            os.remove(out_path)
        except Exception:
            pass