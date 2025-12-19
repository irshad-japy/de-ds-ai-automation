from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile


def merge_hook_full_video(hook_video: str | Path, full_video: str | Path) -> Path:
    """
    Prepend hook_video to full_video and return the final merged video path.

    Output is saved next to full_video in:
      <full_video_parent>/output/merge_video/<full_video_stem>_with_hook.mp4
    """
    hook_video = Path(hook_video)
    full_video = Path(full_video)

    if not hook_video.exists():
        raise FileNotFoundError(f"Hook video not found: {hook_video}")
    if not full_video.exists():
        raise FileNotFoundError(f"Full video not found: {full_video}")

    out_dir = full_video.parent / "output" / "merge_video"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{full_video.stem}_with_hook.mp4"

    # Create concat list file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        # concat demuxer requires: file 'path'
        f.write(f"file '{hook_video.resolve().as_posix()}'\n")
        f.write(f"file '{full_video.resolve().as_posix()}'\n")
        list_path = Path(f.name)

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_path),
            # Re-encode to avoid “non-monotonous DTS”, fps mismatch, etc.
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_path),
        ]
        subprocess.run(cmd, check=True)
        return out_path
    finally:
        # cleanup temp file
        if list_path.exists():
            list_path.unlink(missing_ok=True)

# Example usage
if __name__ == "__main__":
    merged = merge_hook_full_video(
        hook_video="output/hooks/hook_10s.mp4",
        full_video="output/merge_video/video_with_bg.mp4",
    )
    print("Merged video:", merged)
