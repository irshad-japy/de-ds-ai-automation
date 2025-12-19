"""
xtts_voice_helper.py

Reusable XTTS v2 helpers:
- clone_voice_once(...)  → one-time cloning from ref audio
- tts_with_cached_speaker(...) → reuse cached speaker_id

Global defaults:
- MODEL_NAME      (from XTTS_MODEL_NAME or XTTS v2 default)
- DEFAULT_LANGUAGE (from XTTS_LANGUAGE, default "en")
- Device auto-detect with optional XTTS_DEVICE override
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache
from app.utils.file_cache import cache_file
import torch
from TTS.api import TTS
import logging
from app.utils.structured_logging import get_logger, log_message
logger = get_logger("xtts_voice_helper", logging.DEBUG)

# =====================================================
# Global configuration
# =====================================================

# Hugging Face / Coqui XTTS v2 model
MODEL_NAME: str = os.getenv(
    "XTTS_MODEL_NAME",
    "tts_models/multilingual/multi-dataset/xtts_v2",
)

# Default language for all calls, can be overridden per-call
DEFAULT_LANGUAGE: str = os.getenv("XTTS_LANGUAGE", "en")

# Optional root output dir (used only if you pass relative paths)
OUTPUT_ROOT: Path = Path(os.getenv("XTTS_OUTPUT_ROOT", "output")).expanduser()

def _ensure_parent_dir(path: Path) -> None:
    """Create parent directory for the given file path if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)

def _get_device() -> str:
    """
    Decide whether to use GPU or CPU.

    Priority:
    1. XTTS_DEVICE environment variable: "cuda", "cpu", or "auto" (default)
    2. If auto: use CUDA when available, else CPU.
    """
    env_device = os.getenv("XTTS_DEVICE", "cuda").lower()

    if env_device == "cpu":
        device = "cpu"
    elif env_device == "cuda":
        if torch.cuda.is_available():
            device = "cuda"
        else:
            print("[XTTS] XTTS_DEVICE=cuda but CUDA is not available. Falling back to CPU.")
            device = "cpu"
    else:  # auto
        device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"[XTTS] Using device: {device}")
    return device

@lru_cache(maxsize=2)
def _get_tts(model_name: str) -> TTS:
    """
    Load the XTTS model once per process and cache it.

    The cache key is the model_name. Device selection is based on
    the current XTTS_DEVICE / CUDA availability at first call.
    """
    device = _get_device()
    print(f"[XTTS] Loading model '{model_name}' on device '{device}'")
    tts = TTS(model_name).to(device)
    return tts

def _normalize_language(language: Optional[str]) -> str:
    """
    Normalize the language code, falling back to DEFAULT_LANGUAGE.
    """
    lang = (language or DEFAULT_LANGUAGE).strip()
    if not lang:
        # Final safety net
        lang = "en"
    return lang

def _normalize_output_dir(output_dir: Optional[str | Path]) -> Path:
    """
    Resolve the output directory.

    - If output_dir is absolute → use it as-is.
    - If output_dir is relative or None → place under OUTPUT_ROOT.
    """
    if output_dir is None:
        out_dir = OUTPUT_ROOT
    else:
        out_dir = Path(output_dir).expanduser()
        if not out_dir.is_absolute():
            out_dir = OUTPUT_ROOT / out_dir

    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

# =====================================================
# Public API
# =====================================================

def clone_voice_once(
    ref_audio_path: str | Path,
    speaker_id: str,
    output_dir: Optional[str | Path] = None,
    clone_text: str = "This is my cloned voice created by XTTS.",
    language: Optional[str] = None,
    model_name: Optional[str] = None,
) -> Path:
    """
    ONE-TIME operation to create / update a speaker embedding.

    - ref_audio_path: WAV/OGG/MP3 file with your voice (clean, 5–30 seconds)
    - speaker_id: identifier that you will reuse later (e.g. "IrshadVoice01")
    - output_dir: where to write a test file (default: OUTPUT_ROOT)
    - clone_text: any short text to validate the new voice
    - language: language code for this test (default: DEFAULT_LANGUAGE)
    - model_name: override XTTS model name (default: MODEL_NAME)

    After this is called once (per model cache), you can reuse speaker_id
    from any project as long as they use the same model + local cache.
    """
    model_name = model_name or MODEL_NAME
    language = _normalize_language(language)

    ref_audio = Path(ref_audio_path).expanduser()
    if not ref_audio.is_file():
        raise FileNotFoundError(f"Reference audio not found: {ref_audio}")

    out_dir = _normalize_output_dir(output_dir)
    test_out = out_dir / f"{speaker_id}_clone_check_{language}.wav"

    tts = _get_tts(model_name)
    tts.tts_to_file(
        text=clone_text,
        speaker_wav=[str(ref_audio)],
        speaker=speaker_id,
        language=language,
        file_path=str(test_out),
    )

    print(f"Voice cloned and cached under speaker_id='{speaker_id}'")
    print(f"Test file written: {test_out}")
    return test_out

@cache_file("output/cache", namespace="audio", ext=".wav", out_arg="out_path")
def tts_with_cached_speaker(
    text: str,
    speaker_id: str,
    out_path: str | Path,
    language: Optional[str] = None,
    model_name: Optional[str] = None,
) -> Path:
    """
    Reuse an ALREADY-CACHED speaker_id.

    - No ref_audio_path required here
    - Assumes clone_voice_once() (or similar) was run earlier, on this
      machine, for this model_name and speaker_id.
    """
    model_name = model_name or MODEL_NAME
    language = _normalize_language(language)

    out_file = Path(out_path)
    # If out_path is relative, place it under OUTPUT_ROOT
    if not out_file.is_absolute():
        out_file = OUTPUT_ROOT / out_file
    _ensure_parent_dir(out_file)

    print(f'final output path: {out_path}')

    tts = _get_tts(model_name)
    tts.tts_to_file(
        text=text,
        speaker=speaker_id,  # only the ID, uses cached embedding
        language=language,
        file_path=str(out_file),
    )

    return out_file
