"""
python test/voice_to_video_merge_debug.py
"""

import os
import subprocess
import ffmpeg
from moviepy import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from pathlib import Path

# ---------------------------------------------------------------
# user-defined inputs
VIDEO_FILE = "C:/Users/erirs/projects/ird-projects/de_ds_ai_automation/ai-youtube-automation/assets/video/my_demo_video.mp4"           # original video file
DUBBED_AUDIO = "C:/Users/erirs/projects/ird-projects/de_ds_ai_automation/ai-youtube-automation/output/demo_audio.wav"  # new dubbed audio
LANG_CODE = "hi"   # optional metadata tag

# automatically derive output path
video_path = Path(VIDEO_FILE)
output_dir = video_path.parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# dynamically name output file based on input video name + lang
video_stem = video_path.stem  # e.g., "my_demo_video"
OUTPUT_FILE = output_dir / f"{video_stem}_{LANG_CODE}_merged.mp4"

# ---------------------------------------------------------------
def get_duration(path):
    probe = ffmpeg.probe(path)
    return float(probe["format"]["duration"])

def align_audio_duration(video_path, audio_path):
    """If durations differ slightly, stretch audio to match video."""
    dur_v = get_duration(video_path)
    dur_a = get_duration(audio_path)
    print(f"[INFO] Video duration: {dur_v:.2f}s | Audio duration: {dur_a:.2f}s")

    if abs(dur_v - dur_a) > 0.25:
        print(f"[WARN] Durations differ by {abs(dur_v - dur_a):.2f}s — stretching audio...")
        ratio = dur_v / dur_a
        sound = AudioSegment.from_file(audio_path)
        # small time-stretch without pitch change
        new_sound = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * ratio)
        }).set_frame_rate(sound.frame_rate)
        tmp_aligned = audio_path.replace(".wav", "_aligned.wav")
        new_sound.export(tmp_aligned, format="wav")
        print(f"[INFO] Audio stretched by ratio {ratio:.4f}")
        return tmp_aligned
    else:
        print("[OK] Audio duration already matches video.")
        return audio_path

def merge_audio_video(video_path, audio_path, output_path, lang_code=""):
    """Replace original video audio with dubbed audio."""
    cmd = [
        "ffmpeg",
        "-y",                        # overwrite output
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",              # copy video stream
        "-map", "0:v:0",             # first input's video
        "-map", "1:a:0",             # second input's audio
        "-shortest",
    ]
    if lang_code:
        cmd += ["-metadata:s:a:0", f"language={lang_code}"]
    cmd += [output_path]

    # log command
    print("\n[DEBUG] FFmpeg command:")
    print(" ".join(cmd), "\n")

    # run
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] FFmpeg stderr:\n", result.stderr)
        raise RuntimeError("FFmpeg merge failed.")
    else:
        print("[OK] Merge completed successfully.")
        print(f"[INFO] Output file: {output_path}")

    # verify durations
    dur_v = get_duration(video_path)
    dur_out = get_duration(output_path)
    print(f"[VERIFY] Input video: {dur_v:.2f}s | Output merged: {dur_out:.2f}s")

# ---------------------------------------------------------------
if __name__ == "__main__":
    try:
        print("[STEP 1] Checking durations...")
        aligned_audio = align_audio_duration(VIDEO_FILE, DUBBED_AUDIO)

        print("[STEP 2] Merging video and dubbed audio...")
        merge_audio_video(VIDEO_FILE, aligned_audio, OUTPUT_FILE, LANG_CODE)

        print("[DONE] Verify playback manually for lip-sync and drift.")
    except Exception as e:
        print(f"[FATAL] {e}")
