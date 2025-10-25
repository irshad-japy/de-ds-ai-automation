
from __future__ import annotations
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip

def replace_audio_track(video_path: Path, audio_path: Path, out_path: Path):
    with VideoFileClip(str(video_path)) as v:
        with AudioFileClip(str(audio_path)) as a:
            out = v.set_audio(a)
            out.write_videofile(str(out_path), codec="libx264", audio_codec="aac")
