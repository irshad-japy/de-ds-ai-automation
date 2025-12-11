"""
python -m app.services.voice_to_video_merge
Reusable helpers to align audio with video and merge using ffmpeg.
"""

# app/services/voice_to_video_merge.py

from pathlib import Path
import subprocess
import ffmpeg
from pydub import AudioSegment
import os

def get_duration(path: str | Path) -> float:
    path = str(path)
    probe = ffmpeg.probe(path)
    return float(probe["format"]["duration"])

def align_audio_duration(video_path: str | Path, audio_path: str | Path) -> Path:
    video_path = Path(video_path)
    audio_path = Path(audio_path)

    dur_v = get_duration(video_path)
    dur_a = get_duration(audio_path)

    print(f"[INFO] Video duration: {dur_v:.2f}s | Audio duration: {dur_a:.2f}s")

    if abs(dur_v - dur_a) <= 0.25:
        print("[OK] Audio duration already matches video closely.")
        return audio_path

    print(f"[WARN] Durations differ by {abs(dur_v - dur_a):.2f}s — stretching audio...")
    ratio = dur_v / dur_a

    sound = AudioSegment.from_file(audio_path)
    new_sound = sound._spawn(
        sound.raw_data,
        overrides={"frame_rate": int(sound.frame_rate * ratio)},
    ).set_frame_rate(sound.frame_rate)

    aligned_path = audio_path.with_name(f"{audio_path.stem}_aligned.wav")
    new_sound.export(aligned_path, format="wav")

    print(f"[INFO] Audio stretched by ratio {ratio:.4f}")
    print(f"[INFO] Aligned audio saved at: {aligned_path}")
    return aligned_path

def merge_audio_video(
    video_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    lang_code: str = "en",
) -> Path:
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-metadata:s:a:0", f"language={lang_code}",
        str(output_path),
    ]

    print("\n[DEBUG] FFmpeg command:")
    print(" ".join(cmd), "\n")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] FFmpeg stderr:\n", result.stderr)
        raise RuntimeError("FFmpeg merge failed.")
    else:
        print("[OK] Merge completed successfully.")
        print(f"[INFO] Output file: {output_path}")

    dur_v = get_duration(video_path)
    dur_out = get_duration(output_path)
    print(f"[VERIFY] Input video: {dur_v:.2f}s | Output merged: {dur_out:.2f}s")

    return output_path


# ✅ SIMPLE PUBLIC FUNCTION (only 2 parameters)
def merge_voice_and_video(
    video_path: str | Path,
    audio_path: str | Path,
) -> Path:
    """
    Simple helper:
    - output file: <video_dir>/<video_stem>_merged.mp4
    - language: 'en'
    - audio duration: always aligned to video
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)

    # Default output: same folder, "<video_name>_merged.mp4"
    # output_path = video_path.with_name(f"{video_path.stem}_merged.mp4")
    output_file = f"{video_path.stem}_merged.mp4"
    output_path = os.path.join('output/merge_video', output_file)

    print("[STEP] Aligning audio duration with video...")
    aligned_audio = align_audio_duration(video_path, audio_path)

    print("[STEP] Merging video and audio...")
    return merge_audio_video(video_path, aligned_audio, output_path, lang_code="en")

if __name__ == "__main__":
    # Example direct usage
    v = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\assets\video\my_demo_video.mp4"
    a = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\output\clone_voice\clone_voice\mcp_server_poc.wav"
    merged = merge_voice_and_video(v, a)
    print("[DONE] Merged file:", merged)
