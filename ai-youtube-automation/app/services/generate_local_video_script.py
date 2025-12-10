"""
python ai-youtube-automation/app/services/generate_local_video_script.py
"""
import os
import datetime
import re
from difflib import SequenceMatcher
from moviepy import VideoFileClip
import whisper

# -------------------------------------------------------
# 🔹 Step 1: Extract Audio from Local Video File
# -------------------------------------------------------
def extract_audio_from_video(video_path: str, output_dir: str = "output") -> str:
    """
    Extracts audio from a local video file and saves as WAV.
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(video_path))[0]}_audio.wav")

    print(f"🎬 Extracting audio from {video_path} ...")
    video_clip = VideoFileClip(video_path)
    video_clip.audio.write_audiofile(audio_path, codec="pcm_s16le")
    video_clip.close()

    print(f"✅ Audio saved at: {audio_path}")
    return audio_path

# -------------------------------------------------------
# 🔹 Step 2: Transcribe Audio using Whisper
# -------------------------------------------------------
def transcribe_audio(audio_path: str, model_name="base") -> list:
    """
    Transcribes audio file using OpenAI Whisper model.
    Returns a list of text fragments with timestamps.
    """
    print(f"🧠 Loading Whisper model '{model_name}' ...")
    model = whisper.load_model(model_name)

    print(f"🎧 Transcribing audio from {audio_path} ...")
    result = model.transcribe(audio_path)
    segments = result.get("segments", [])
    print(f"✅ Transcription completed. {len(segments)} segments extracted.")
    return segments

# -------------------------------------------------------
# 🔹 Step 3: Clean and Deduplicate Transcript
# -------------------------------------------------------
def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower().strip(" .!?।")

def merge_transcript_fragments(segments):
    """
    Deduplicate overlapping or repeated fragments using fuzzy similarity.
    """
    merged = []
    last_norm = ""
    last_end = 0.0

    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].replace("\n", " ").strip()
        norm = normalize(text)
        sim = SequenceMatcher(None, last_norm, norm).ratio() if last_norm else 0

        if sim > 0.8 and (start - last_end < 2.5):
            continue

        merged.append(text)
        last_norm, last_end = norm, end

    full_text = " ".join(merged)
    full_text = re.sub(r"\s+([,.!?;:])", r"\1", full_text)
    full_text = re.sub(r"\s+", " ", full_text)
    full_text = re.sub(r"([।.!?])\s+", r"\1\n", full_text)
    return full_text.strip()

# -------------------------------------------------------
# 🔹 Step 4: Save Transcript to TXT
# -------------------------------------------------------
def save_transcript(text: str, video_path: str) -> str:
    os.makedirs("output", exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]
    file_path = os.path.join("output", f"{base}_transcript_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"✅ Transcript saved to: {file_path}")
    return file_path

# -------------------------------------------------------
# 🔹 Step 5: Full Pipeline
# -------------------------------------------------------
def process_local_video(video_path: str, model_name="base"):
    """
    End-to-end pipeline:
      1. Extract audio
      2. Transcribe speech
      3. Deduplicate and clean
      4. Save to text file
    """
    audio_path = extract_audio_from_video(video_path)
    segments = transcribe_audio(audio_path, model_name)
    cleaned_text = merge_transcript_fragments(segments)
    file_path = save_transcript(cleaned_text, video_path)
    return file_path

# -------------------------------------------------------
# 🔹 Run from CLI
# -------------------------------------------------------
if __name__ == "__main__":
    local_video_path = "C:/Users/ermdi/Videos/Screen Recordings/Screen Recording 2025-12-08 200452.mp4"  # 🔁 change this to your local file
    process_local_video(local_video_path, model_name="small")