"""
python -m app.services.avatar_overlay
"""

from pathlib import Path
import subprocess
import os


def add_avatar_pip(
    base_video: str | Path,
    avatar_video: str | Path,
    output_path: str | Path,
    scale: float = 0.25,
    position: str = "bottom-right",
) -> Path:
    """
    Overlay avatar_video as picture-in-picture on base_video.

    - scale: fraction of original avatar width (0.25 = 25%)
    - position: "bottom-right", "bottom-left", "top-right", "top-left"
    """
    base_video = Path(base_video)
    avatar_video = Path(avatar_video)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Choose overlay expression based on position
    if position == "bottom-right":
        x_expr = "W-w-40"
        y_expr = "H-h-40"
    elif position == "bottom-left":
        x_expr = "40"
        y_expr = "H-h-40"
    elif position == "top-right":
        x_expr = "W-w-40"
        y_expr = "40"
    else:  # top-left
        x_expr = "40"
        y_expr = "40"

    filter_complex = (
        f"[1:v]scale=iw*{scale}:-1[avatar];"
        f"[0:v][avatar]overlay={x_expr}:{y_expr}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(base_video),
        "-i", str(avatar_video),
        "-filter_complex", filter_complex,
        "-map", "0:a?", "-c:a", "copy",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-shortest",
        str(output_path),
    ]

    print("[DEBUG] Overlay command:\n", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] ffmpeg stderr:\n", result.stderr)
        raise RuntimeError("Avatar overlay failed")

    print(f"[OK] Avatar overlay created: {output_path}")
    return output_path


if __name__ == "__main__":
    base = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\output\merge_video\my_demo_video_merged.mp4"
    avatar = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\output\merge_video\my_demo_video_merged.mp4"
    out = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\output\merge_video\my_demo_video_avatar.mp4"
    add_avatar_pip(base, avatar, out)
