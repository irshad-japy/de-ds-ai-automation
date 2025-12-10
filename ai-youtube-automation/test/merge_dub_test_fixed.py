"""
python .\test\merge_dub_test_fixed.py
"""

import os
import subprocess
import ffmpeg
from moviepy import VideoFileClip, AudioFileClip
from pydub import AudioSegment

# ---------------------------------------------------------------
# user-defined inputs
VIDEO_FILE = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\assets\video\final_merge_14_scene.mp4"
DUBBED_AUDIO = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\assets\audio\bg_lofi_01.mp3"
OUTPUT_FILE = r"C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\ai-youtube-automation\output\final_merge_14_scene_voice.mp4"
LANG_CODE = "en"
# ---------------------------------------------------------------

def get_duration(path):
    """Return duration of audio or video file."""
    probe = ffmpeg.probe(path)
    return float(probe["format"]["duration"])

def align_audio_to_video(video_path, audio_path):
    """Stretch or compress audio to exactly match video length."""
    dur_v = get_duration(video_path)
    dur_a = get_duration(audio_path)
    print(f"[INFO] Video duration: {dur_v:.2f}s | Audio duration: {dur_a:.2f}s")

    ratio = dur_v / dur_a
    print(f"[ACTION] Adjusting audio speed by ratio {ratio:.4f}")

    sound = AudioSegment.from_file(audio_path)
    new_sound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * ratio)
    }).set_frame_rate(sound.frame_rate)

    tmp_path = os.path.splitext(audio_path)[0] + "_adjusted.wav"
    new_sound.export(tmp_path, format="wav")
    print(f"[OK] Exported adjusted audio → {tmp_path}")
    return tmp_path

def merge_audio_video(video_path, audio_path, output_path, lang_code=""):
    """Merge audio and video perfectly aligned in length."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",  # stops at shortest track (now both equal length)
    ]
    if lang_code:
        cmd += ["-metadata:s:a:0", f"language={lang_code}"]
    cmd += [output_path]

    print("\n[DEBUG] FFmpeg command:\n" + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("[ERROR] FFmpeg stderr:\n", result.stderr)
        raise RuntimeError("FFmpeg merge failed.")
    else:
        print("[OK] Merge completed successfully.")
        dur_out = get_duration(output_path)
        print(f"[VERIFY] Final merged file duration: {dur_out:.2f}s")

# ---------------------------------------------------------------
if __name__ == "__main__":
    try:
        print("[STEP 1] Aligning audio duration to match video...")
        adjusted_audio = align_audio_to_video(VIDEO_FILE, DUBBED_AUDIO)

        print("[STEP 2] Merging video with adjusted audio...")
        merge_audio_video(VIDEO_FILE, adjusted_audio, OUTPUT_FILE, LANG_CODE)

        print("\n[DONE] Check final video playback — durations now perfectly match.")
    except Exception as e:
        print(f"[FATAL] {e}")
