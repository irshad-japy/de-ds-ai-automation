
from __future__ import annotations
import subprocess, tempfile, difflib, re
from pathlib import Path
from typing import List
import numpy as np
import cv2, pytesseract
from PIL import Image
from .utils import clean_topic, save_json, get_video_metadata, OUTPUT_DIR, which

def ocr_outline_from_video(src: Path, sample_every: float=1.2, scene_sensitivity: float=0.25, min_line_len: int=10, max_lines: int=16) -> list[str]:
    tmp = Path(tempfile.mkdtemp(prefix="autoscript_"))
    scene_dir = tmp / "scenes"; scene_dir.mkdir(parents=True, exist_ok=True)
    ff = which("ffmpeg")
    frames = []
    if ff:
        cmd = [ff, "-y", "-i", str(src), "-vf", f"select='gt(scene,{scene_sensitivity})',showinfo", "-vsync", "vfr", str(scene_dir / "scene_%05d.png")]
        subprocess.run(cmd, capture_output=True, text=True)
        sample_dir = tmp / "samples"; sample_dir.mkdir(parents=True, exist_ok=True)
        fps = max(0.5, 1.0/max(0.2, sample_every))
        cmd2 = [ff, "-y", "-i", str(src), "-vf", f"fps={fps}", str(sample_dir / "frame_%05d.png")]
        subprocess.run(cmd2, capture_output=True, text=True)
        frames = sorted({*scene_dir.glob("*.png"), *sample_dir.glob("*.png")})

    def similar(a,b): 
        return difflib.SequenceMatcher(a=a.lower(), b=b.lower()).ratio() >= 0.85

    texts: list[str] = []
    for fp in frames[:500]:
        try:
            img = Image.open(fp).convert("L")
            arr = np.array(img)
            _, arr = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(arr, lang="eng")
            lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) >= min_line_len]
            for ln in lines:
                if not any(similar(ln, t) for t in texts):
                    texts.append(ln)
        except Exception:
            continue
    outline = texts[:max_lines] if texts else []
    return outline

def compose_professional_script(topic: str, points: list[str], target_seconds: int, audience: str|None=None, tone: str|None="confident") -> str:
    topic = clean_topic(topic)
    who = f" for {audience}" if audience else ""
    tone_txt = f" in a {tone} tone" if tone else ""
    hook = f"{topic}{who}: here’s a fast, practical walkthrough{tone_txt}."
    value = "You’ll learn what it is, why it matters, and exactly how to do it."
    steps = [f"- {p.strip()}" for p in points if p.strip()][:10] or [
        f"- Step 1: Open {topic}",
        "- Step 2: Configure the key option",
        "- Step 3: Validate and ship"
    ]
    recap = "Recap: follow these steps in order and you’ll avoid the common pitfalls."
    cta = "Pause where needed, replay tricky parts, and try it now."
    draft = "\n".join([hook, value, *steps, recap, cta])
    target_words = max(60, int(2.2 * max(20, target_seconds)))
    words = draft.split()
    if len(words) > target_words:
        draft = " ".join(words[:target_words])
    return draft

def build_autoscript(video_path: Path, sample_every: float, scene_sensitivity: float, target_seconds: int, min_line_len: int, max_lines: int):
    meta = get_video_metadata(video_path)
    outline = ocr_outline_from_video(video_path, sample_every, scene_sensitivity, min_line_len, max_lines)
    script = compose_professional_script(video_path.stem, outline, target_seconds)
    out = {"metadata": meta, "outline": outline or [f"Overview of {video_path.stem}"], "voiceover_script": script}
    dest = OUTPUT_DIR / f"{video_path.stem}_voiceover.json"
    save_json(out, dest)
    return str(dest), out
