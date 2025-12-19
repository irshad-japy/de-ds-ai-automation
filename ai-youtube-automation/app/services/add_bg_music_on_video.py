"""
python -m app.services.add_bg_music_on_video
"""

from __future__ import annotations
import json
import subprocess
from pathlib import Path
from app.utils.file_cache import cache_file
import os

def ffprobe_duration_seconds(media_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(media_path),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(p.stdout)
    return float(data["format"]["duration"])

def video_has_audio_stream(video_path: Path) -> bool:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "json",
        str(video_path),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(p.stdout)
    return bool(data.get("streams"))

@cache_file("output/cache", namespace="video", ext=".mp4", out_arg="out_path")
def add_background_music(video_path: str | Path, music_path: str | Path) -> Path:
    """
    Mix looping background music under existing video audio.

    Output:
      <project_root>/output/final_video/<video_stem>_bg_video<ext>
    """
    music_volume = 0.15
    audio_bitrate = "192k"

    video_path = Path(video_path)
    music_path = Path(music_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not music_path.exists():
        raise FileNotFoundError(f"Music not found: {music_path}")

    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "output" / "final_video"

    out_filename = f"{video_path.stem}_bg_video{video_path.suffix}"
    out_path = Path(os.path.join(str(output_dir), out_filename))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    duration = ffprobe_duration_seconds(video_path)
    has_audio = video_has_audio_stream(video_path)

    if has_audio:
        filter_complex = (
            f"[1:a]volume={music_volume}[bg];"
            f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-stream_loop", "-1", "-i", str(music_path),
            "-t", f"{duration:.3f}",
            "-filter_complex", filter_complex,
            "-map", "0:v:0",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-movflags", "+faststart",
            str(out_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-stream_loop", "-1", "-i", str(music_path),
            "-t", f"{duration:.3f}",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-movflags", "+faststart",
            str(out_path),
        ]

    subprocess.run(cmd, check=True)
    return out_path

if __name__ == "__main__":
    video = r"assets/video/demo_video.mp4"
    music = r"assets/audio/background-music-159125.mp3"
    result = add_background_music(video, music)
    print("Saved:", result)
