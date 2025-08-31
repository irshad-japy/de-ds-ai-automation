import os
import time
from pathlib import Path
from typing import List, Optional

from utils.paths import AUDIO_DIR

# =========================
# ElevenLabs (cloud) utils
# =========================

def _client(api_key: Optional[str] = None):
    api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ELEVENLABS_API_KEY in environment or parameter.")
    try:
        from elevenlabs.client import ElevenLabs
    except Exception:
        raise ImportError("elevenlabs SDK not installed. Add it to poetry dependencies.")
    return ElevenLabs(api_key=api_key)

def _map_output_format(fmt: str) -> str:
    """
    Map simple formats to ElevenLabs accepted values.
    """
    f = (fmt or "mp3").lower()
    if f in ("mp3", "mp3_44100_128"):
        return "mp3_44100_128"
    if f in ("wav", "pcm_16000"):
        # ElevenLabs returns 16k PCM WAV in this profile
        return "pcm_16000"
    # safe default
    return "mp3_44100_128"

def _resolve_voice_id(client, voice_id_or_name: Optional[str]) -> str:
    """
    Accepts an ID, a display name, or None. Returns a valid voice_id.
    Resolution order:
      1) If a valid voice_id was provided, use it.
      2) If ELEVENLABS_DEFAULT_VOICE_ID is set and valid, use it.
      3) If a name was provided, look it up by name.
      4) Fallback to the first voice in the account.
    """
    # 1) Try direct id
    if voice_id_or_name:
        try:
            v = client.voices.get(voice_id_or_name)
            if v and getattr(v, "voice_id", None):
                return v.voice_id
        except Exception:
            # not a valid ID; may be a name → try name resolution below
            pass

    # 2) Try env default id
    env_id = (os.getenv("ELEVENLABS_DEFAULT_VOICE_ID") or "").strip()
    if env_id:
        try:
            v = client.voices.get(env_id)
            if v and getattr(v, "voice_id", None):
                return v.voice_id
        except Exception:
            pass

    # 3) If a name was provided, try match by name
    if voice_id_or_name:
        all_voices = client.voices.get_all().voices or []
        for v in all_voices:
            if v.name.strip().lower() == voice_id_or_name.strip().lower():
                return v.voice_id

    # 4) Fallback: first available voice
    all_voices = client.voices.get_all().voices or []
    if all_voices:
        return all_voices[0].voice_id

    raise RuntimeError(
        "No voices available in your ElevenLabs account. "
        "Create/clone a voice in the dashboard or via the Voice Cloning section."
    )

# -----------------------------
# ElevenLabs: Text-to-Speech
# -----------------------------

def synthesize_elevenlabs(
    text: str,
    voice_id: Optional[str] = None,
    api_key: Optional[str] = None,
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3",
    out_dir: Path = AUDIO_DIR,
) -> str:
    """
    Generate speech via ElevenLabs' TTS API.
    Returns the saved audio file path (str).
    """
    client = _client(api_key=api_key)
    try:
        resolved_voice_id = _resolve_voice_id(client, voice_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        # map simple format to ElevenLabs' expected values
        el_fmt = _map_output_format(output_format)
        ext = "mp3" if el_fmt.startswith("mp3") else "wav"
        out_path = out_dir / f"tts_elevenlabs_{ts}.{ext}"

        # Stream bytes and write to file
        audio = client.text_to_speech.convert(
            voice_id=resolved_voice_id,
            model_id=model_id,
            text=text,
            output_format=el_fmt,
            optimize_streaming_latency="0",
        )
        with open(out_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        return str(out_path)

    except Exception as e:
        # Try to unpack ElevenLabs ApiError for clearer diagnostics
        status = getattr(e, "status_code", None)
        body = getattr(e, "body", None)
        headers = getattr(e, "headers", None)
        if status or body or headers:
            raise RuntimeError(
                f"ElevenLabs TTS failed: status_code={status}, body={body}, headers={headers}"
            ) from e
        raise RuntimeError(f"ElevenLabs TTS failed: {e}") from e

# -----------------------------
# ElevenLabs: Voice Cloning
# -----------------------------

def clone_voice_elevenlabs(
    name: str,
    files: List[str],
    api_key: Optional[str] = None,
    description: str = "Cloned via Gradio app",
) -> str:
    """
    Create a custom/cloned voice in ElevenLabs and return voice_id.
    `files` should be paths to clean speech samples (mp3/wav/m4a, etc.).
    """
    client = _client(api_key=api_key)

    # Open uploaded files
    with_files = [open(p, "rb") for p in files if p]
    try:
        resp = client.voices.add(name=name, files=with_files, description=description)
    finally:
        for fh in with_files:
            try:
                fh.close()
            except Exception:
                pass

    voice_id = getattr(resp, "voice_id", None) or getattr(resp, "id", None)
    if not voice_id and isinstance(resp, dict):
        voice_id = resp.get("voice_id") or resp.get("id")
    if not voice_id:
        raise RuntimeError(f"Failed to create voice: {resp}")
    return voice_id

# -------------------------------------------
# Local option via Transformers Parler-TTS
# -------------------------------------------

def synthesize_parler(
    text: str,
    model_id: str = "parler-tts/parler-tts-mini-v1",
    out_dir: Path = AUDIO_DIR,
    sample_rate: int = 22050,
) -> str:
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError("Transformers not installed for Parler-TTS pipeline.") from e

    try:
        import soundfile as sf
    except Exception as e:
        raise RuntimeError("soundfile is required. `poetry add soundfile`.") from e

    out_dir.mkdir(parents=True, exist_ok=True)
    tts = pipeline("text-to-speech", model=model_id)  # <-- Uses Parler model
    audio = tts(text)
    data = audio["audio"]
    sr = int(audio.get("sampling_rate", sample_rate))
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / f"tts_parler_{ts}.wav"
    sf.write(out_path, data, sr)
    return str(out_path)
# -------------------------------------------
# Simple offline fallback using pyttsx3
# -------------------------------------------

def synthesize_pyttsx3(text: str, out_dir: Path = AUDIO_DIR) -> str:
    """
    Offline system TTS. Works with SAPI5 (Windows), NSSpeechSynthesizer (macOS).
    Saves to WAV using save_to_file.
    """
    try:
        import pyttsx3
    except Exception as e:
        raise RuntimeError("pyttsx3 not installed.") from e

    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    wav_path = out_dir / f"tts_pyttsx3_{ts}.wav"

    engine = pyttsx3.init()
    engine.save_to_file(text, str(wav_path))
    engine.runAndWait()
    return str(wav_path)
