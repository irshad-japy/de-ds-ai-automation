"""
python -m app.services.merge_thumbnail_video
"""

from __future__ import annotations
import json
import subprocess
from pathlib import Path
from app.utils.file_cache import cache_file
import logging

from app.utils.structured_logging import get_logger, log_message
logger = get_logger("merge_thumbnail_video", logging.DEBUG)

out_dir = Path("output/merge_video")

def _run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\nCommand: {' '.join(cmd)}\n\nSTDERR:\n{p.stderr}")

def _ffprobe_json(video_path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_streams", "-show_format",
        str(video_path)
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed:\n{p.stderr}")
    return json.loads(p.stdout)

def _get_av_props(meta: dict) -> tuple[int, int, float, bool, int, str]:
    """
    Return (width, height, fps, has_audio, audio_sample_rate, audio_channel_layout)
    """
    v_stream = None
    a_stream = None

    for s in meta.get("streams", []):
        if s.get("codec_type") == "video" and v_stream is None:
            v_stream = s
        if s.get("codec_type") == "audio" and a_stream is None:
            a_stream = s

    if not v_stream:
        raise ValueError("No video stream found.")

    width = int(v_stream.get("width"))
    height = int(v_stream.get("height"))

    fr = v_stream.get("r_frame_rate") or v_stream.get("avg_frame_rate") or "30/1"
    num, den = fr.split("/")
    fps = float(num) / float(den) if float(den) != 0 else 30.0
    if fps <= 0 or fps > 240:
        fps = 30.0

    has_audio = a_stream is not None
    if has_audio:
        sr = int(a_stream.get("sample_rate") or 44100)
        layout = a_stream.get("channel_layout")
        if not layout:
            ch = int(a_stream.get("channels") or 2)
            layout = "mono" if ch == 1 else "stereo"
    else:
        sr = 44100
        layout = "stereo"

    return width, height, fps, has_audio, sr, layout

@cache_file("output/cache", namespace="video", ext=".mp4", out_arg="out_path")
def add_image_invideo(video_path: str | Path, image_path: str | Path, intro_second=0.01) -> Path:
    video_path = Path(video_path)
    image_path = Path(image_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    meta = _ffprobe_json(video_path)
    w, h, fps, has_audio, sr, layout = _get_av_props(meta)

    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{video_path.stem}_with_thumb{video_path.suffix}"
    intro_path = out_dir / f"{video_path.stem}_intro_tmp.mp4"

    # IMPORTANT: 0.01s at 30fps can become 0 frames.
    # Force at least 1 frame duration.
    intro_second = float(intro_second)
    min_duration = 1.0 / float(fps)
    if intro_second < min_duration:
        intro_second = min_duration

    # 1) Create intro video from image (scaled/padded to match the video)
    # Create silent audio that MATCHES the original audio (if any)
    intro_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-f", "lavfi", "-t", str(intro_second),
        "-i", f"anullsrc=channel_layout={layout}:sample_rate={sr}",
        "-t", str(intro_second),
        "-vf",
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,format=yuv420p",
        "-r", str(fps),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        str(intro_path)
    ]
    _run(intro_cmd)

    # 2) Concatenate intro + original video
    if has_audio:
        # Normalize BOTH video SAR (and timestamps) so concat never fails
        fc = (
            f"[0:v]setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v0];"
            f"[1:v]setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v1];"
            f"[0:a]aresample={sr},aformat=channel_layouts={layout},asetpts=PTS-STARTPTS[a0];"
            f"[1:a]aresample={sr},aformat=channel_layouts={layout},asetpts=PTS-STARTPTS[a1];"
            f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"
        )

        concat_cmd = [
            "ffmpeg", "-y",
            "-i", str(intro_path),
            "-i", str(video_path),
            "-filter_complex", fc,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            str(out_path)
        ]
    else:
        # No audio in original: concat only video, normalize SAR
        fc = (
            f"[0:v]setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v0];"
            f"[1:v]setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v1];"
            f"[v0][v1]concat=n=2:v=1:a=0[v]"
        )

        concat_cmd = [
            "ffmpeg", "-y",
            "-i", str(intro_path),
            "-i", str(video_path),
            "-filter_complex", fc,
            "-map", "[v]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(out_path)
        ]

    _run(concat_cmd)

    try:
        intro_path.unlink(missing_ok=True)
    except Exception:
        pass

    return out_path

if __name__ == "__main__":
    video_path = "assets/video/demo_video.mp4"
    disclaimer_path = "assets/image/demo_disclaimer.png"

    out = add_image_invideo(video_path, disclaimer_path)
    logger.info(f"✅ Saved: {out.resolve()}")
