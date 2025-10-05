"""
python tests/moviepy_poc.py make-sample --out output/sample.mp4 --dur 10
MoviePy POC — one-file toolbox
(See usage examples at the top of this file.)
"""

import argparse, math, json
from pathlib import Path
from typing import Tuple, List
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (VideoFileClip, AudioFileClip, ColorClip, VideoClip,
                            concatenate_videoclips, vfx, AudioArrayClip)

def ensure_parent(path: Path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True); return path

def load_font(size=48):
    try: return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        try: return ImageFont.truetype("DejaVuSans.ttf", size=size)
        except Exception: return ImageFont.load_default()

def draw_text_on_frame(frame_rgb: np.ndarray, text: str, pos: Tuple[str,str], margin=(24,24)) -> np.ndarray:
    img = Image.fromarray(frame_rgb); draw = ImageDraw.Draw(img); font = load_font(48)
    w, h = img.size; tw, th = draw.textbbox((0,0), text, font=font)[2:]
    x_align, y_align = pos
    x = {"left": margin[0], "center": (w - tw)//2, "right": w - tw - margin[0]}.get(x_align, (w - tw)//2)
    y = {"top": margin[1], "center": (h - th)//2, "bottom": h - th - margin[1]}.get(y_align, h - th - margin[1])
    draw.text((x+2,y+2), text, fill=(0,0,0), font=font); draw.text((x,y), text, fill=(255,255,255), font=font)
    return np.array(img)

def act_make_sample(out: Path, dur: float=8, fps: int=30, size=(1280,720)):
    W,H = size; ensure_parent(out)
    def make_frame(t):
        r = int(60 + 50*np.sin(2*np.pi*t/3)); g = int(60 + 50*np.sin(2*np.pi*t/2)); b = int(60 + 50*np.sin(2*np.pi*t/5))
        frame = np.full((H,W,3), (r,g,b), dtype=np.uint8)
        x = int((W-200)*(0.5+0.4*np.sin(2*np.pi*t/4))); y = int((H-200)*(0.5+0.4*np.cos(2*np.pi*t/6)))
        frame[y:y+200, x:x+200] = (255-r, 100, 255-b)
        return draw_text_on_frame(frame, f"Sample t={t:0.1f}s", ("center","bottom"))
    clip = VideoClip(make_frame, duration=dur).with_fps(fps)
    sr = 44100; tt = np.linspace(0, dur, int(sr*dur), endpoint=False)
    wave = 0.2*np.sin(2*np.pi*(440 + (880-440)*tt/dur)*tt) if dur>0 else np.zeros(1, np.float32)
    audio = AudioArrayClip(wave.astype(np.float32).reshape(-1,1), fps=sr); clip = clip.with_audio(audio)
    clip.write_videofile(str(out), codec="libx264", audio_codec="aac"); clip.close(); print("Wrote", out)

def act_meta(video: Path):
    with VideoFileClip(str(video)) as v:
        info = dict(duration=v.duration, size=v.size, fps=v.fps, audio_fps=getattr(v.audio, "fps", None))
    print(json.dumps(info, indent=2))

def act_cut(video: Path, start: float, end: float, out: Path):
    ensure_parent(out)
    with VideoFileClip(str(video)) as v:
        v.subclip(start, end).write_videofile(str(out), codec="libx264", audio_codec="aac")
    print("Wrote", out)

def act_speed(video: Path, factor: float, out: Path):
    ensure_parent(out)
    with VideoFileClip(str(video)) as v:
        v.fx(vfx.speedx, factor).write_videofile(str(out), codec="libx264", audio_codec="aac")
    print("Wrote", out)

def act_resize(video: Path, width: int, out: Path):
    ensure_parent(out)
    with VideoFileClip(str(video)) as v:
        v.resize(width=width).write_videofile(str(out), codec="libx264", audio_codec="aac")
    print("Wrote", out)

def act_crop(video: Path, x1:int,y1:int,x2:int,y2:int, out: Path):
    ensure_parent(out)
    with VideoFileClip(str(video)) as v:
        v.fx(vfx.crop, x1=x1,y1=y1,x2=x2,y2=y2).write_videofile(str(out), codec="libx264", audio_codec="aac")
    print("Wrote", out)

def act_replace_audio(video: Path, out: Path, audio: Path=None, beep: int=0, dur: float=None):
    ensure_parent(out)
    with VideoFileClip(str(video)) as v:
        if audio and Path(audio).exists():
            a = AudioFileClip(str(audio))
        else:
            a = None
            if beep:
                d = dur or v.duration; sr = 44100
                t = np.linspace(0, d, int(sr*d), endpoint=False)
                wave = 0.2*np.sin(2*np.pi*520*t)
                a = AudioArrayClip(wave.astype(np.float32).reshape(-1,1), fps=sr)
        outclip = v.with_audio(a) if a else v.without_audio()
        outclip.write_videofile(str(out), codec="libx264", audio_codec="aac")
        if a: a.close()
    print("Wrote", out)

def act_overlay_text(video: Path, text: str, pos: str, out: Path):
    ensure_parent(out)
    xalign, yalign = ("center","bottom")
    if "," in pos: xs, ys = pos.split(",",1); xalign, yalign = xs.strip(), ys.strip()
    with VideoFileClip(str(video)) as v:
        def f(t):
            return draw_text_on_frame(v.get_frame(t), text, (xalign, yalign))
        over = VideoClip(f, duration=v.duration).with_fps(v.fps).with_audio(v.audio)
        over.write_videofile(str(out), codec="libx264", audio_codec="aac")
    print("Wrote", out)

def act_thumbs(video: Path, times, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    with VideoFileClip(str(video)) as v:
        from PIL import Image
        for t in times:
            t = max(0.0, min(v.duration, t))
            Image.fromarray(v.get_frame(t)).save(out_dir / f"thumb_{t:0.2f}s.png")
    print("Wrote", out_dir)

def act_gif(video: Path, start: float, end: float, fps: int, out: Path):
    ensure_parent(out)
    with VideoFileClip(str(video)) as v:
        v.subclip(start, end).write_gif(str(out), fps=fps, program="ffmpeg")
    print("Wrote", out)

def main():
    import argparse
    ap = argparse.ArgumentParser(description="MoviePy POC toolbox")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("make-sample"); s.add_argument("--out", required=True); s.add_argument("--dur", type=float, default=8)
    s = sub.add_parser("meta"); s.add_argument("--video", required=True)
    s = sub.add_parser("cut"); s.add_argument("--video", required=True); s.add_argument("--start", type=float, required=True); s.add_argument("--end", type=float, required=True); s.add_argument("--out", required=True)
    s = sub.add_parser("speed"); s.add_argument("--video", required=True); s.add_argument("--factor", type=float, required=True); s.add_argument("--out", required=True)
    s = sub.add_parser("resize"); s.add_argument("--video", required=True); s.add_argument("--width", type=int, required=True); s.add_argument("--out", required=True)
    s = sub.add_parser("crop"); s.add_argument("--video", required=True); s.add_argument("--x1", type=int, required=True); s.add_argument("--y1", type=int, required=True); s.add_argument("--x2", type=int, required=True); s.add_argument("--y2", type=int, required=True); s.add_argument("--out", required=True)
    s = sub.add_parser("replace-audio"); s.add_argument("--video", required=True); s.add_argument("--audio"); s.add_argument("--out", required=True); s.add_argument("--beep", type=int, default=0); s.add_argument("--dur", type=float)
    s = sub.add_parser("overlay-text"); s.add_argument("--video", required=True); s.add_argument("--text", required=True); s.add_argument("--pos", default="center,bottom"); s.add_argument("--out", required=True)
    s = sub.add_parser("thumbnails"); s.add_argument("--video", required=True); s.add_argument("--times", required=True); s.add_argument("--dir", required=True)
    s = sub.add_parser("gif"); s.add_argument("--video", required=True); s.add_argument("--start", type=float, required=True); s.add_argument("--end", type=float, required=True); s.add_argument("--fps", type=int, default=12); s.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.cmd == "make-sample":
        act_make_sample(Path(args.out), dur=args.dur)
    elif args.cmd == "meta":
        act_meta(Path(args.video))
    elif args.cmd == "cut":
        act_cut(Path(args.video), args.start, args.end, Path(args.out))
    elif args.cmd == "speed":
        act_speed(Path(args.video), args.factor, Path(args.out))
    elif args.cmd == "resize":
        act_resize(Path(args.video), args.width, Path(args.out))
    elif args.cmd == "crop":
        act_crop(Path(args.video), args.x1,args.y1,args.x2,args.y2, Path(args.out))
    elif args.cmd == "replace-audio":
        act_replace_audio(Path(args.video), Path(args.out), Path(args.audio) if args.audio else None, beep=args.beep, dur=args.dur)
    elif args.cmd == "overlay-text":
        act_overlay_text(Path(args.video), args.text, args.pos, Path(args.out))
    elif args.cmd == "thumbnails":
        times = [float(x) for x in str(args.times).split(",")]
        act_thumbs(Path(args.video), times, Path(args.dir))
    elif args.cmd == "gif":
        act_gif(Path(args.video), args.start, args.end, args.fps, Path(args.out))
    else:
        raise SystemExit("Unknown comman")

if __name__ == "__main__":
    main()
