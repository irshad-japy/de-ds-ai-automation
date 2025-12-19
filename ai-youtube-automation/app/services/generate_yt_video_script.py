"""
python ai-youtube-automation/app/services/generate_yt_video_script.py
"""

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from fastapi import HTTPException
import re, os, datetime
import logging
from app.utils.structured_logging import get_logger, log_message
logger = get_logger("generate_yt_video_script", logging.DEBUG)

# -------------------------------------------------------
# 🔹 Extract YouTube Video ID
# -------------------------------------------------------
def extract_video_id(url: str) -> str:
    patterns = [r"v=([A-Za-z0-9_-]{11})", r"youtu\.be/([A-Za-z0-9_-]{11})"]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    raise HTTPException(status_code=400, detail="Invalid YouTube URL")

# -------------------------------------------------------
# 🔹 Normalize Text for Comparison
# -------------------------------------------------------
def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower().strip(" .!?।")

# -------------------------------------------------------
# 🔹 Merge Transcript with De-duplication
# -------------------------------------------------------
def merge_transcript_fragments(transcript):
    merged = []

    for item in transcript:

        text = item.text

        merged.append(text)

    full_text = " ".join(merged)
    full_text = re.sub(r"\s+([,.!?;:])", r"\1", full_text)
    full_text = re.sub(r"\s+", " ", full_text)
    full_text = re.sub(r"([।.!?])\s+", r"\1\n", full_text)
    return full_text.strip()

# -------------------------------------------------------
# 🔹 Fetch and Save Transcript
# -------------------------------------------------------
def fetch_and_save_transcript(url: str, languages=None):
    if languages is None:
        languages = ['de', 'en', 'hi']

    video_id = extract_video_id(url)
    logger.info(f"🔹 Fetching transcript for video_id={video_id} in {languages}")

    try:
        ytt_api = YouTubeTranscriptApi()
        # Direct fetch using provided languages
        fragments = ytt_api.fetch(video_id, languages=languages)
        if not fragments:
            raise ValueError("Transcript is empty — subtitles may be disabled.")
    except TranscriptsDisabled:
        raise HTTPException(status_code=400, detail="Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transcript: {e}")

    text = merge_transcript_fragments(fragments)

    # Save cleaned transcript
    os.makedirs("output", exist_ok=True)
    file_path = os.path.join("output", f"{video_id}_transcript_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    
    logger.info(f"✅ Transcript saved successfully: {file_path}")
    return file_path

# -------------------------------------------------------
# 🔹 Run Directly (For Manual Testing)
# -------------------------------------------------------
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=ROmtgqTefAw&t=2s"
    fetch_and_save_transcript(url, languages=['de', 'en', 'hi'])
