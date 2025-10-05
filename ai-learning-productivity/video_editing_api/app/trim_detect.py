
from __future__ import annotations
import subprocess, shutil
from pathlib import Path
from typing import List, Tuple
from moviepy import VideoFileClip, concatenate_videoclips

def detect_silence(in_video: Path, silence_db: int=-35, min_s: float=1.2) -> list[tuple[float,float]]:
    ff = shutil.which("ffmpeg"); assert ff
    cmd = [ff, "-i", str(in_video), "-af", f"silencedetect=noise={silence_db}dB:d={min_s}", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stderr or "") + (p.stdout or "")
    starts, ends = [], []
    for line in out.splitlines():
        if "silence_start" in line:
            try: starts.append(float(line.split("silence_start:")[1].strip()))
            except: pass
        if "silence_end" in line:
            try:
                parts = line.split("silence_end:")[1].split("|")[0].strip()
                ends.append(float(parts))
            except: pass
    return list(zip(starts, ends))

def detect_black(in_video: Path, pix_thresh: float=0.10, dur: float=0.8) -> list[tuple[float,float]]:
    ff = shutil.which("ffmpeg"); assert ff
    vf = f"blackdetect=d={dur}:pic_th={pix_thresh}"
    cmd = [ff, "-i", str(in_video), "-vf", vf, "-an", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stderr or "") + (p.stdout or "")
    starts, ends = [], []
    for ln in out.splitlines():
        if "black_start:" in ln:
            try: starts.append(float(ln.split("black_start:")[1].split()[0]))
            except: pass
        if "black_end:" in ln:
            try: ends.append(float(ln.split("black_end:")[1].split()[0]))
            except: pass
    return list(zip(starts, ends))

def invert_ranges(duration: float, drop_ranges: list[tuple[float,float]], pad: float=0.10) -> list[tuple[float,float]]:
    if not drop_ranges:
        return [(0.0, duration)]
    drops = sorted(drop_ranges)
    merged = []
    cur_s, cur_e = drops[0]
    for s,e in drops[1:]:
        if s <= cur_e + 1e-3:
            cur_e = max(cur_e, e)
        else:
            merged.append((cur_s, cur_e)); cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))

    keeps = []
    prev = 0.0
    for s,e in merged:
        if s - prev > 0.25:
            keeps.append((max(0, prev - pad), max(prev, s - pad)))
        prev = e
    if duration - prev > 0.25:
        keeps.append((prev + pad, duration))
    keeps = [(max(0,t1), min(duration,t2)) for (t1,t2) in keeps if t2 - t1 > 0.25]
    return keeps

def cut_keep_segments(in_video: Path, out_video: Path, keeps: list[tuple[float,float]]):
    with VideoFileClip(str(in_video)) as clip:
        parts = [clip.subclip(a,b) for (a,b) in keeps if b>a]
        if not parts:
            parts = [clip.subclip(0, min(2, clip.duration))]
        final = concatenate_videoclips(parts, method="compose")
        final.write_videofile(str(out_video), codec="libx264", audio_codec="aac", threads=4)
        for p in parts: p.close()

def auto_trim_blank(in_video: Path, out_video: Path) -> list[tuple[float,float]]:
    with VideoFileClip(str(in_video)) as c:
        dur = c.duration
    sil = detect_silence(in_video)
    blk = detect_black(in_video)
    drops = sil + blk
    keeps = invert_ranges(dur, drops, pad=0.10)
    cut_keep_segments(in_video, out_video, keeps)
    return keeps
