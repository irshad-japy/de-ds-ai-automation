
"""
python -m app.services.generate_hooks
Local "professional-ish" hook generator:
- Transcribe audio into timestamped segments
- Search only the INTRO (first N seconds)
- Score sliding windows (10–20s) and pick the best
- Cut that exact window from the original video
"""

from __future__ import annotations
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from faster_whisper import WhisperModel
import torch

# -----------------------------
# Scoring helpers
# -----------------------------
def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def hook_score_text(text: str) -> int:
    """
    Score a whole window of text (multi-sentence).
    Higher score => more hook-like.
    """
    t = normalize_text(text)
    score = 0

    # Positive signals
    triggers = [
        "if you", "your", "stuck", "problem", "fail", "error", "fix", "avoid",
        "stop", "mistake", "secret", "simple", "fast", "today", "now",
        "most people", "one thing", "the reason", "here s", "here's",
        "in", "minutes", "seconds"
    ]
    score += sum(1 for k in triggers if k in t)

    # Bonus for question marks (curiosity)
    if "?" in text:
        score += 2

    # Bonus for numbers/time
    if re.search(r"\b\d+\b", t):
        score += 2

    # Penalize slow intros / greetings
    slow = ["hi guys", "welcome back", "like and subscribe", "in this video we will", "today we are going to"]
    score -= sum(3 for k in slow if k in t)

    # Prefer concise
    words = t.split()
    if 18 <= len(words) <= 55:
        score += 2
    elif len(words) < 10:
        score -= 2
    elif len(words) > 80:
        score -= 2

    return score

# -----------------------------
# Whisper segments
# -----------------------------
@dataclass
class SegTS:
    start: float
    end: float
    text: str

def transcribe_segments(audio_path: Path, model_size: str = "small") -> List[SegTS]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # compute_type: better defaults
    compute_type = "float16" if device == "cuda" else "int8"

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = model.transcribe(
        str(audio_path),
        beam_size=5,
        word_timestamps=False  # segment-level is enough + more stable for windows
    )

    out: List[SegTS] = []
    for seg in segments:
        txt = (seg.text or "").strip()
        if not txt:
            continue
        out.append(SegTS(start=float(seg.start), end=float(seg.end), text=txt))
    return out

# -----------------------------
# Window selection (professional-ish)
# -----------------------------
def pick_best_hook_window(
    segments: List[SegTS],
    intro_search_max_sec: float = 90.0,
    min_len: float = 10.0,
    max_len: float = 20.0,
    target_len: float = 15.0,
) -> Tuple[float, float, int, str]:
    """
    Returns (start, end, score, window_text)
    """
    # only look in intro
    intro = [s for s in segments if s.start <= intro_search_max_sec]
    if not intro:
        raise RuntimeError("No transcript segments found in intro window.")

    best_start, best_end, best_score, best_text = 0.0, 0.0, -10**9, ""

    n = len(intro)
    for i in range(n):
        start = intro[i].start
        text_parts = []
        end = start

        # expand window by adding segments until we hit min_len
        for j in range(i, n):
            text_parts.append(intro[j].text)
            end = intro[j].end
            dur = end - start

            if dur < min_len:
                continue
            if dur > max_len:
                break

            window_text = " ".join(text_parts).strip()
            score = hook_score_text(window_text)

            # Prefer duration close to target_len
            dur_penalty = abs(dur - target_len) * 2.0
            score_adj = int(score - dur_penalty)

            if score_adj > best_score:
                best_start, best_end, best_score, best_text = start, end, score_adj, window_text

    return best_start, best_end, best_score, best_text

# -----------------------------
# ffmpeg cut
# -----------------------------
def ffmpeg_cut(video_path: Path, start: float, end: float, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}",
        "-to", f"{end:.3f}",
        "-i", str(video_path),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        str(out_path)
    ] 
    subprocess.run(cmd, check=True)

def make_hook_clip(
    video_path: str | Path,
    audio_path: str | Path,
    script_text: str = "",  # optional now
    out_path: str | Path = "output/hooks/hook_15s.mp4",
    min_len: float = 10.0,
    max_len: float = 20.0,
    target_len: float = 15.0,
    intro_search_max_sec: float = 90.0,
    whisper_model: str = "small",
    pad_before: float = 0.2,
    pad_after: float = 0.4,
) -> dict:
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    out_path = Path(out_path)

    if not video_path.exists():
        raise FileNotFoundError(video_path)
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    segments = transcribe_segments(audio_path, model_size=whisper_model)
    start, end, score, text = pick_best_hook_window(
        segments=segments,
        intro_search_max_sec=intro_search_max_sec,
        min_len=min_len,
        max_len=max_len,
        target_len=target_len,
    )

    start = max(0.0, start - pad_before)
    end = end + pad_after

    ffmpeg_cut(video_path, start, end, out_path)

    return {
        "hook_text_window": text,
        "hook_score": score,
        "start_sec": round(start, 3),
        "end_sec": round(end, 3),
        "duration_sec": round(end - start, 3),
        "out_path": str(out_path),
        "intro_search_max_sec": intro_search_max_sec,
    }

if __name__ == "__main__":
    # Example
    meta = make_hook_clip(
        video_path="output/merge_video/video_with_bg.mp4",
        audio_path="output/clone_voice/deepak_en_aligned.wav",
        script_text="",
        out_path="output/hooks/hook_15s.mp4",
        min_len=10,
        max_len=20,
        target_len=15,
        intro_search_max_sec=90,
        whisper_model="small",
    )
    print(meta)
