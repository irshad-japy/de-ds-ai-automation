"""
python -m app.services.voice_to_video_merge

Reusable helpers to align/cut audio/video duration and merge using ffmpeg.

cut_mode behavior (recommended):
- "none" / "default": KEEP FULL VIDEO length (pad audio with silence if shorter)
- "video": if video > audio -> trim video tail to audio length
- "audio": if audio > video -> trim audio tail to video length

No stretching.
"""

from __future__ import annotations

from pathlib import Path
from app.utils.file_cache import cache_file
import subprocess
import ffmpeg
from pydub import AudioSegment
from typing import Tuple
import logging
from app.utils.structured_logging import get_logger, log_message
logger = get_logger("voice_to_video_merge", logging.DEBUG)

# How close durations can be before we say "they're basically equal"
DURATION_TOLERANCE = 0.10  # seconds (set small >0 to avoid tiny differences)

# -------------------------------------------------------
# Duration helpers
# -------------------------------------------------------
def get_duration(path: str | Path) -> float:
    """Return media duration in seconds using ffprobe (stable, no ffmpeg-python needed)."""
    path = str(path)
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    try:
        out = subprocess.check_output(cmd, text=True).strip()
        return float(out)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed for {path}: {e.output}") from e
    except Exception as e:
        raise RuntimeError(f"Could not parse duration for {path}: {e}") from e

# -------------------------------------------------------
# Trim helpers
# -------------------------------------------------------
def trim_audio_to_duration(audio_path: Path, target_duration: float) -> Path:
    """Trim audio from end to target_duration. Writes <stem>_trimmed.wav"""
    logger.info(f"[STEP] Trimming audio to {target_duration:.2f}s")

    sound = AudioSegment.from_file(audio_path)
    target_ms = int(target_duration * 1000)

    if target_ms <= 0:
        raise ValueError("Target duration for audio must be > 0")

    trimmed = sound[:target_ms]
    trimmed_path = audio_path.with_name(f"{audio_path.stem}_trimmed.wav")
    trimmed.export(trimmed_path, format="wav")

    dur_trimmed = get_duration(trimmed_path)
    logger.info(f"[INFO] Audio trimmed: {dur_trimmed:.2f}s -> {trimmed_path}")
    return trimmed_path

def trim_video_to_duration(video_path: Path, target_duration: float) -> Path:
    """Trim video from end to target_duration. Writes <stem>_trimmed.mp4"""
    logger.info(f"[STEP] Trimming video to {target_duration:.2f}s")

    trimmed_path = video_path.with_name(f"{video_path.stem}_trimmed.mp4")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-t",
        f"{target_duration:.3f}",
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        str(trimmed_path),
    ]

    logger.info("\n[DEBUG] FFmpeg trim video command:")
    logger.info(" ".join(cmd), "\n")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.info("[ERROR] FFmpeg stderr (trim video):\n", result.stderr)
        raise RuntimeError("FFmpeg video trim failed.")

    dur_trimmed = get_duration(trimmed_path)
    logger.info(f"[INFO] Video trimmed: {dur_trimmed:.2f}s -> {trimmed_path}")
    return trimmed_path

# -------------------------------------------------------
# Decide trimming based on cut_mode
# -------------------------------------------------------
def prepare_media_for_merge(
    video_path: str | Path,
    audio_path: str | Path,
    cut_mode: str = "none",
) -> Tuple[Path, Path]:
    """
    Decide whether to cut video or audio based on cut_mode.

    cut_mode options:
        - "video": if video > audio, cut extra video from end.
        - "audio": if audio > video, cut extra audio from end.
        - "none"/"default": don't pre-trim (we will keep video length at merge step).
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)

    mode = (cut_mode or "none").lower().strip()
    if mode == "default":
        mode = "none"

    dur_v = get_duration(video_path)
    dur_a = get_duration(audio_path)

    logger.info(f"[INFO] Original durations -> Video: {dur_v:.2f}s | Audio: {dur_a:.2f}s")
    logger.info(f"[INFO] cut_mode = {mode!r}")

    final_video = video_path
    final_audio = audio_path

    # If durations are close, don't bother cutting.
    if abs(dur_v - dur_a) <= DURATION_TOLERANCE:
        logger.info("[OK] Durations already close, no trimming needed.")
        return final_video, final_audio

    if mode in {"video", "cut_video"} and dur_v > dur_a:
        final_video = trim_video_to_duration(video_path, dur_a)

    elif mode in {"audio", "cut_audio"} and dur_a > dur_v:
        final_audio = trim_audio_to_duration(audio_path, dur_v)

    else:
        logger.info("[INFO] No pre-trim applied (mode='none' or condition not met).")

    return final_video, final_audio

# -------------------------------------------------------
# Merge (core)
# -------------------------------------------------------
def merge_audio_video(
    video_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    lang_code: str = "en",
    keep_video_length: bool = False,
    pad_audio: bool = True,
) -> Path:
    """
    Merge video and audio into a single MP4.

    If keep_video_length=True:
      - output duration = video duration
      - if audio shorter, pad with silence (apad) so it doesn't cut early
      - uses -t <video_duration> to force output length

    If keep_video_length=False:
      - uses -shortest (output ends when shortest stream ends)
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",               # safer container audio than raw wav in mp4
        "-b:a",
        "192k",
        "-metadata:s:a:0",
        f"language={lang_code}",
    ]

    if keep_video_length:
        vid_dur = get_duration(video_path)

        # pad audio with silence (only matters when audio shorter)
        if pad_audio:
            cmd += ["-af", "apad"]

        # force output duration to video duration
        cmd += ["-t", f"{vid_dur:.3f}"]

        # IMPORTANT: do NOT use -shortest here
    else:
        cmd += ["-shortest"]

    cmd += [str(output_path)]

    logger.info("\n[DEBUG] FFmpeg merge command:")
    logger.info(" ".join(cmd), "\n")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.info("[ERROR] FFmpeg stderr (merge):\n", result.stderr)
        raise RuntimeError("FFmpeg merge failed.")
    else:
        logger.info("[OK] Merge completed successfully.")
        logger.info(f"[INFO] Output file: {output_path}")

    dur_v = get_duration(video_path)
    dur_a = get_duration(audio_path)
    dur_out = get_duration(output_path)
    logger.info(f"[VERIFY] Video in: {dur_v:.2f}s | Audio in: {dur_a:.2f}s | Output: {dur_out:.2f}s")

    return output_path

# -------------------------------------------------------
# Public function
# -------------------------------------------------------
@cache_file("output/cache", namespace="video", ext=".mp4", out_arg="out_path")
def merge_voice_and_video(
    video_path: str | Path,
    audio_path: str | Path,
    cut_mode: str = "none",
    lang_code: str = "en",
) -> Path:
    """
    - output: output/merge_video/<video_stem>_merged.mp4

    cut_mode:
      - "video": if video > audio -> trim video (output ends at audio length)
      - "audio": if audio > video -> trim audio (output ends at video length)
      - "none"/"default": KEEP FULL VIDEO length (pad audio with silence)
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)

    output_root = Path("output") / "merge_video"
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / f"{video_path.stem}_merged.mp4"

    logger.info("[STEP] Preparing media (optional cutting based on cut_mode)...")
    final_video, final_audio = prepare_media_for_merge(video_path, audio_path, cut_mode=cut_mode)

    # ✅ Recommendation:
    # For cut_mode="none", keep the video length (do NOT use -shortest)
    mode = (cut_mode or "none").lower().strip()
    keep_video_length = mode in {"none", "default"}

    logger.info(f"[STEP] Merging video and audio... (keep_video_length={keep_video_length})")
    return merge_audio_video(
        final_video,
        final_audio,
        output_path,
        lang_code=lang_code,
        keep_video_length=keep_video_length,
        pad_audio=True,
    )

# -------------------------------------------------------
# CLI usage
# -------------------------------------------------------
if __name__ == "__main__":
    v = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\assets\video\demo_video.mp4"
    a = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\output\clone_voice\deepak_en.wav"

    # ✅ Case 1: cut extra video if video longer
    # merged = merge_voice_and_video(v, a, cut_mode="video")

    # ✅ Case 2: cut extra audio if audio longer
    # merged = merge_voice_and_video(v, a, cut_mode="audio")

    # ✅ Case 3 (recommended): keep video length, pad audio with silence
    merged = merge_voice_and_video(v, a, cut_mode="none")

    logger.info("[DONE] Merged file:", merged)
