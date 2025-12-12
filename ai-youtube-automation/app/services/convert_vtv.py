"""
python -m app.services.convert_vtv

Adds VOICE CONVERSION helpers (audio->audio) in addition to XTTS TTS.
Voice conversion uses a separate model and separate cache from XTTS.
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

import torch
from TTS.api import TTS

# =====================================================
# Global configuration
# =====================================================

# XTTS v2 model (text -> speech, voice cloning)
MODEL_NAME: str = os.getenv(
    "XTTS_MODEL_NAME",
    "tts_models/multilingual/multi-dataset/xtts_v2",
)

DEFAULT_LANGUAGE: str = os.getenv("XTTS_LANGUAGE", "en")
OUTPUT_ROOT: Path = Path(os.getenv("XTTS_OUTPUT_ROOT", "output")).expanduser()

# Voice Conversion model (audio -> audio, same content, different voice)
# Good defaults from Coqui docs: openvoice_v2 / freevc24 / knnvc
VC_MODEL_NAME: str = os.getenv(
    "VC_MODEL_NAME",
    "voice_conversion_models/multilingual/multi-dataset/openvoice_v2",
)

def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def _get_device() -> str:
    env_device = os.getenv("XTTS_DEVICE", "auto").lower()

    if env_device == "cpu":
        device = "cpu"
    elif env_device == "cuda":
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            print("[XTTS] XTTS_DEVICE=cuda but CUDA not available -> CPU fallback.")
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"[TTS] Using device: {device}")
    return device

@lru_cache(maxsize=4)
def _get_model(model_name: str) -> TTS:
    device = _get_device()
    print(f"[TTS] Loading model '{model_name}' on '{device}'")
    return TTS(model_name).to(device)

def _normalize_language(language: Optional[str]) -> str:
    lang = (language or DEFAULT_LANGUAGE).strip()
    return lang or "en"

def _normalize_output_dir(output_dir: Optional[str | Path]) -> Path:
    if output_dir is None:
        out_dir = OUTPUT_ROOT
    else:
        out_dir = Path(output_dir).expanduser()
        if not out_dir.is_absolute():
            out_dir = OUTPUT_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

# =====================================================
# XTTS (text -> speech) existing API
# =====================================================

def clone_voice_once(
    ref_audio_path: str | Path,
    speaker_id: str,
    output_dir: Optional[str | Path] = None,
    clone_text: str = "This is my cloned voice created by XTTS.",
    language: Optional[str] = None,
    model_name: Optional[str] = None,
) -> Path:
    model_name = model_name or MODEL_NAME
    language = _normalize_language(language)

    ref_audio = Path(ref_audio_path).expanduser()
    if not ref_audio.is_file():
        raise FileNotFoundError(f"Reference audio not found: {ref_audio}")

    out_dir = _normalize_output_dir(output_dir)
    test_out = out_dir / f"{speaker_id}_clone_check_{language}.wav"

    tts = _get_model(model_name)
    tts.tts_to_file(
        text=clone_text,
        speaker_wav=[str(ref_audio)],
        speaker=speaker_id,
        language=language,
        file_path=str(test_out),
    )
    print(f"✅ XTTS voice cloned/cached under speaker_id='{speaker_id}' -> {test_out}")
    return test_out

def tts_with_cached_speaker(
    text: str,
    speaker_id: str,
    out_path: str | Path,
    language: Optional[str] = None,
    model_name: Optional[str] = None,
) -> Path:
    model_name = model_name or MODEL_NAME
    language = _normalize_language(language)

    out_file = Path(out_path).expanduser()
    if not out_file.is_absolute():
        out_file = OUTPUT_ROOT / out_file
    _ensure_parent_dir(out_file)

    tts = _get_model(model_name)
    tts.tts_to_file(
        text=text,
        speaker=speaker_id,
        language=language,
        file_path=str(out_file),
    )
    print(f"✅ XTTS TTS generated using speaker_id='{speaker_id}' -> {out_file}")
    return out_file

# =====================================================
# NEW: Voice Conversion (audio -> audio) API
# =====================================================

def cache_vc_target_voice_once(
    target_wav: str | Path,
    vc_speaker_id: str,
    output_dir: Optional[str | Path] = None,
    vc_model_name: Optional[str] = None,
) -> Path:
    """
    ONE-TIME: cache your target voice for VC models.

    - target_wav: your voice sample wav (clean)
    - vc_speaker_id: id to reuse later (VC cache, separate from XTTS cache!)
    """
    vc_model_name = vc_model_name or VC_MODEL_NAME

    target_wav = Path(target_wav).expanduser()
    if not target_wav.is_file():
        raise FileNotFoundError(f"Target wav not found: {target_wav}")

    out_dir = _normalize_output_dir(output_dir)
    test_out = out_dir / f"{vc_speaker_id}_vc_cache_check.wav"

    vc = _get_model(vc_model_name)

    # Easiest way to “prime” cache: convert the same audio into itself once.
    vc.voice_conversion_to_file(
        source_wav=str(target_wav),
        target_wav=str(target_wav),
        speaker=vc_speaker_id,     # <--- this enables caching for later calls
        file_path=str(test_out),
    )

    print(f"✅ VC target voice cached under vc_speaker_id='{vc_speaker_id}' -> {test_out}")
    return test_out

def voice_to_voice(
    source_wav: str | Path,
    target_wav: str | Path,
    out_path: str | Path,
    vc_model_name: Optional[str] = None,
) -> Path:
    vc_model_name = vc_model_name or VC_MODEL_NAME

    source_wav = Path(source_wav).expanduser()
    target_wav = Path(target_wav).expanduser()
    if not source_wav.is_file():
        raise FileNotFoundError(f"Source wav not found: {source_wav}")
    if not target_wav.is_file():
        raise FileNotFoundError(f"Target wav not found: {target_wav}")

    out_file = Path(out_path).expanduser()
    if not out_file.is_absolute():
        out_file = OUTPUT_ROOT / out_file
    _ensure_parent_dir(out_file)

    vc = _get_model(vc_model_name)

    # ✅ VC requires both source + target wav
    vc.voice_conversion_to_file(
        source_wav=str(source_wav),
        target_wav=str(target_wav),
        file_path=str(out_file),
    )
    print(f"✅ Voice converted -> {out_file}")
    return out_file

import json

VC_MAP_FILE = OUTPUT_ROOT / "vc_targets.json"

def register_vc_target(vc_speaker_id: str, target_wav: str | Path) -> None:
    target_wav = str(Path(target_wav).expanduser())
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    data = {}
    if VC_MAP_FILE.exists():
        data = json.loads(VC_MAP_FILE.read_text(encoding="utf-8"))
    data[vc_speaker_id] = target_wav
    VC_MAP_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✅ Registered VC target: {vc_speaker_id} -> {target_wav}")

def voice_to_voice_with_speaker_id(
    source_wav: str | Path,
    vc_speaker_id: str,
    out_path: str | Path,
    vc_model_name: Optional[str] = None,
) -> Path:
    if not VC_MAP_FILE.exists():
        raise RuntimeError("vc_targets.json not found. Call register_vc_target() first.")
    data = json.loads(VC_MAP_FILE.read_text(encoding="utf-8"))
    if vc_speaker_id not in data:
        raise KeyError(f"vc_speaker_id '{vc_speaker_id}' not registered in vc_targets.json")

    return voice_to_voice(
        source_wav=source_wav,
        target_wav=data[vc_speaker_id],   # ✅ still passes target_wav internally
        out_path=out_path,
        vc_model_name=vc_model_name,
    )


def main():
    # English
    voice_to_voice_with_speaker_id(
        source_wav="C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/clone_voice/deepak_en.wav",
        vc_speaker_id="IrshadVC02",
        out_path="output/converted.wav",
    )

if __name__ == "__main__":
    
    # once time to generate speaker_id or voice
    # cache_vc_target_voice_once(
    #     target_wav="C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/clone_voice/elevanlabs_1.wav",
    #     vc_speaker_id="IrshadVC01",
    # )

    # or once time

    # register_vc_target("IrshadVC02", "C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/IrshadVC01_vc_cache_check.wav")

    # everytime
    main()
    
    # use direct source audio to target audio conversion
    # voice_to_voice(
    #     source_wav="C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/IrshadVC01_vc_cache_check.wav",
    #     target_wav="C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/clone_voice/deepak_hi.wav",
    #     out_path="output/converted.wav",
    # )


