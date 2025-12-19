"""
python app/services/generate_local_video_script.py
Better video->audio->Whisper transcription with safer merging (no aggressive fuzzy dedupe).
"""

import os
import re
import datetime
import subprocess
from pathlib import Path
import whisper
import logging

from app.utils.structured_logging import get_logger, log_message

logger = get_logger("generate_local_video_script", logging.DEBUG)

# -------------------------------------------------------
# 🔹 Step 1: Extract Audio (FFmpeg) -> mono 16k wav
# -------------------------------------------------------
def extract_audio_from_video(
    video_path: str,
    output_dir: str = "output",
    sample_rate: int = 16000,
    mono: bool = True,
    normalize_audio: bool = True,
) -> str:
    """
    Extract audio from video using ffmpeg. Produces clean mono 16k WAV for Whisper.
    """
    video_path = str(video_path)
    os.makedirs(output_dir, exist_ok=True)

    base = Path(video_path).stem
    audio_path = os.path.join(output_dir, f"{base}_audio.wav")

    # Audio filter: loudnorm helps when volume is low / inconsistent
    af = []
    if normalize_audio:
        af.append("loudnorm")
    af_str = ",".join(af) if af else None

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1" if mono else "2",
        "-ar", str(sample_rate),
        "-c:a", "pcm_s16le",
    ]
    if af_str:
        cmd += ["-af", af_str]
    cmd += [audio_path]

    logger.info(f"🎬 Extracting audio via ffmpeg...\n➡️  {video_path}\n➡️  {audio_path}")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger.info(f"✅ Audio saved at: {audio_path}")
    return audio_path


# -------------------------------------------------------
# 🔹 Step 2: Transcribe using Whisper (better params)
# -------------------------------------------------------
def transcribe_audio(
    audio_path: str,
    model_name: str = "small",
    language: str | None = None,          # e.g. "en", "hi" (None = auto-detect)
    task: str = "transcribe",             # or "translate"
) -> list:
    """
    Returns Whisper segments (list of dicts).
    """
    logger.info(f"🧠 Loading Whisper model '{model_name}' ...")
    model = whisper.load_model(model_name)

    logger.info(f"🎧 Transcribing audio...\n➡️  {audio_path}")
    result = model.transcribe(
        audio_path,
        language=language,
        task=task,
        verbose=False,

        # These reduce repetition / looping:
        condition_on_previous_text=False,
        temperature=0.0,

        # Quality improvements (a bit slower, but better):
        beam_size=5,
        best_of=5,

        # Filters (helps cut garbage segments):
        no_speech_threshold=0.6,
        compression_ratio_threshold=2.4,
        logprob_threshold=-1.0,
    )

    segments = result.get("segments", [])
    logger.info(f"✅ Transcription completed. {len(segments)} segments extracted.")
    return segments

# -------------------------------------------------------
# 🔹 Step 3: Safe merge (no aggressive fuzzy dedupe)
# -------------------------------------------------------
def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def _remove_word_overlap(prev: str, curr: str, max_overlap_words: int = 12) -> str:
    """
    If curr starts with the last N words of prev, remove that overlap.
    Much safer than fuzzy similarity for short phrases.
    """
    prev_words = prev.split()
    curr_words = curr.split()
    max_n = min(max_overlap_words, len(prev_words), len(curr_words))

    for n in range(max_n, 0, -1):
        if prev_words[-n:] == curr_words[:n]:
            return " ".join(curr_words[n:])
    return curr

def merge_transcript_segments(segments: list) -> str:
    merged_parts: list[str] = []
    prev_text = ""

    for seg in segments:
        text = _normalize_spaces(seg.get("text", ""))
        if not text:
            continue

        # Skip likely non-speech (Whisper provides this)
        if seg.get("no_speech_prob", 0.0) > 0.75:
            continue

        # Remove overlap with previous chunk (common in Whisper outputs)
        cleaned = _remove_word_overlap(prev_text, text)

        # If after removing overlap it becomes empty, skip
        cleaned = cleaned.strip()
        if not cleaned:
            continue

        merged_parts.append(cleaned)
        prev_text = (prev_text + " " + cleaned).strip()

    full_text = " ".join(merged_parts)
    full_text = re.sub(r"\s+([,.!?;:])", r"\1", full_text)
    full_text = re.sub(r"\s+", " ", full_text).strip()

    # Add line breaks after sentence ends for readability
    full_text = re.sub(r"([।.!?])\s+", r"\1\n", full_text)
    return full_text.strip()

# -------------------------------------------------------
# 🔹 Step 4: Save Transcript
# -------------------------------------------------------
def save_transcript(text: str, video_path: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    base = Path(video_path).stem
    file_path = os.path.join(output_dir, f"{base}_transcript_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")

    logger.info(f"✅ Transcript saved to: {file_path}")
    return file_path

# -------------------------------------------------------
# 🔹 Step 5: Full Pipeline
# -------------------------------------------------------
def process_local_video(
    video_path: str,
    model_name: str = "small",
    language: str | None = None,   # try "en" or "hi" if auto-detect is wrong
    task: str = "transcribe",
) -> str:
    audio_path = extract_audio_from_video(video_path)
    segments = transcribe_audio(audio_path, model_name=model_name, language=language, task=task)

    # Debug tip: logger.info first few segments to verify Whisper output BEFORE merging
    logger.info("\n--- DEBUG: First 5 raw segments ---")
    for s in segments[:5]:
        logger.info(f"[{s.get('start'):.2f}-{s.get('end'):.2f}] {s.get('text','').strip()} (no_speech={s.get('no_speech_prob',0):.2f})")
    logger.info("--- END DEBUG ---\n")

    cleaned_text = merge_transcript_segments(segments)
    return save_transcript(cleaned_text, video_path)

# -------------------------------------------------------
# 🔹 Run from CLI
# -------------------------------------------------------
if __name__ == "__main__":
    local_video_path = r"C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/assets/video/demo_video.mp4"

    # If your audio is Hindi, try language="hi"
    process_local_video(local_video_path, model_name="small", language=None, task="transcribe")
