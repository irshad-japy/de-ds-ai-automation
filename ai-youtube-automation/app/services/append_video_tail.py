"""
python -m app.services.append_video_tail
"""

from __future__ import annotations
import json
import subprocess
from pathlib import Path

out_dir = Path("output/merge_video")
AUDIO_SR = 44100
AUDIO_LAYOUT = "stereo"

def _run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:/nCommand: {' '.join(cmd)}/n/nSTDERR:/n{p.stderr}")

def _ffprobe_json(video_path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_streams", "-show_format",
        str(video_path)
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed:/n{p.stderr}")
    return json.loads(p.stdout)

def _get_video_props(meta: dict) -> tuple[int, int, float, bool, float]:
    """Return (width, height, fps, has_audio, duration_seconds)."""
    v_stream = None
    has_audio = False

    for s in meta.get("streams", []):
        if s.get("codec_type") == "video" and v_stream is None:
            v_stream = s
        if s.get("codec_type") == "audio":
            has_audio = True

    if not v_stream:
        raise ValueError("No video stream found.")

    width = int(v_stream.get("width"))
    height = int(v_stream.get("height"))

    fr = v_stream.get("r_frame_rate") or v_stream.get("avg_frame_rate") or "30/1"
    num, den = fr.split("/")
    fps = float(num) / float(den) if float(den) != 0 else 30.0
    if fps <= 0 or fps > 240:
        fps = 30.0

    dur = 0.0
    try:
        dur = float(meta.get("format", {}).get("duration") or 0.0)
    except Exception:
        dur = 0.0

    return width, height, fps, has_audio, dur

def append_video_to_end(full_video: str | Path, tail_video: str | Path) -> Path:
    full_video = Path(full_video)
    tail_video = Path(tail_video)

    if not full_video.exists():
        raise FileNotFoundError(f"Full video not found: {full_video}")
    if not tail_video.exists():
        raise FileNotFoundError(f"Tail video not found: {tail_video}")

    out_dir.mkdir(parents=True, exist_ok=True)

    full_meta = _ffprobe_json(full_video)
    tail_meta = _ffprobe_json(tail_video)

    tw, th, tfps, full_has_audio, full_dur = _get_video_props(full_meta)
    _,  _,  _,     tail_has_audio, tail_dur = _get_video_props(tail_meta)

    out_path = out_dir / f"{full_video.stem}_plus_tail{full_video.suffix}"

    # Always normalize video to full video's w/h/fps and yuv420p for maximum compatibility
    v0 = (
        f"[0:v]scale={tw}:{th}:force_original_aspect_ratio=decrease,"
        f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={tfps},format=yuv420p,setpts=PTS-STARTPTS[v0]"
    )
    v1 = (
        f"[1:v]scale={tw}:{th}:force_original_aspect_ratio=decrease,"
        f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={tfps},format=yuv420p,setpts=PTS-STARTPTS[v1]"
    )

    want_audio = full_has_audio or tail_has_audio

    filter_parts = [v0, v1]

    # Build audio chains
    if want_audio:
        # Full audio
        if full_has_audio:
            a0 = f"[0:a]aformat=channel_layouts={AUDIO_LAYOUT}:sample_rates={AUDIO_SR},aresample={AUDIO_SR},asetpts=PTS-STARTPTS[a0]"
        else:
            # Silence for full segment duration
            d0 = full_dur if full_dur > 0 else 0.001
            a0 = f"anullsrc=channel_layout={AUDIO_LAYOUT}:sample_rate={AUDIO_SR},atrim=0:{d0},asetpts=PTS-STARTPTS[a0]"

        # Tail audio
        if tail_has_audio:
            a1 = f"[1:a]aformat=channel_layouts={AUDIO_LAYOUT}:sample_rates={AUDIO_SR},aresample={AUDIO_SR},asetpts=PTS-STARTPTS[a1]"
        else:
            # Silence for tail segment duration
            d1 = tail_dur if tail_dur > 0 else 0.001
            a1 = f"anullsrc=channel_layout={AUDIO_LAYOUT}:sample_rate={AUDIO_SR},atrim=0:{d1},asetpts=PTS-STARTPTS[a1]"

        filter_parts += [a0, a1]
        filter_parts.append("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
        filter_complex = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(full_video),
            "-i", str(tail_video),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(out_path),
        ]
    else:
        filter_parts.append("[v0][v1]concat=n=2:v=1:a=0[v]")
        filter_complex = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(full_video),
            "-i", str(tail_video),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(out_path),
        ]

    _run(cmd)
    return out_path

if __name__ == "__main__":
    # Example usage (update paths)
    full_video_path = "C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/final_video/demo_video_bg_video.mp4"
    tail_video_path = "C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/final_video/demo_video_bg_video.mp4"

    out = append_video_to_end(full_video_path, tail_video_path)
    print(f"✅ Saved: {out.resolve()}")
