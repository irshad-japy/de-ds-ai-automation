"""
python ai-youtube-automation/app/services/yt-transcript-api.py
"""

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from difflib import SequenceMatcher
import re, datetime, os
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    import re
    patterns = [r"v=([A-Za-z0-9_-]{11})", r"youtu\.be/([A-Za-z0-9_-]{11})"]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError("Invalid YouTube URL")


def normalize(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower().strip(' .!?।')


def merge_transcript_fragments(transcript):
    merged = []
    last_norm = ""
    last_end = 0.0

    for item in transcript:
        start = item["start"]
        dur = item.get("duration", 0)
        end = start + dur
        text = item["text"].replace("\n", " ").strip()
        norm = normalize(text)
        sim = SequenceMatcher(None, last_norm, norm).ratio() if last_norm else 0

        if sim > 0.8 and (start - last_end < 2.5):
            continue

        merged.append(text)
        last_norm = norm
        last_end = end

    full_text = " ".join(merged)
    full_text = re.sub(r"\s+([,.!?;:])", r"\1", full_text)
    full_text = re.sub(r"\s+", " ", full_text)
    full_text = re.sub(r"([।.!?])\s+", r"\1\n", full_text)
    return full_text.strip()


def extract_youtube_transcript(url: str, lang_code="hi"):
    video_id = extract_video_id(url)
    print(f"Fetching transcript for {video_id} in language '{lang_code}'...")

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try exact language first
        try:
            transcript = transcript_list.find_transcript([lang_code])
        except Exception:
            # Fallback to translated transcript or auto-generated
            print(f"⚠️ No '{lang_code}' transcript found. Trying auto-generated or translated...")
            transcript = transcript_list.find_manually_created_transcript([lang_code]) \
                         if any(t.is_translatable for t in transcript_list) else transcript_list.find_generated_transcript([lang_code])

        fragments = transcript.fetch()

    except TranscriptsDisabled:
        raise ValueError("❌ Transcripts are disabled for this video.")
    except Exception as e:
        raise ValueError(f"❌ Failed to fetch transcript: {e}")

    text = merge_transcript_fragments(fragments)

    os.makedirs("output", exist_ok=True)
    filename = f"{video_id}_{lang_code}_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
    file_path = os.path.join("output", filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")

    print(f"✅ Transcript saved: {file_path}")
    return file_path


if __name__ == "__main__":
    # url = "https://www.youtube.com/watch?v=GKkU1smMGiA"
    # lang = "hi"
    from youtube_transcript_api import YouTubeTranscriptApi
    video_id = "GKkU1smMGiA"

    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(video_id, languages=['de', 'en', 'hi'])

    # is iterable
    for snippet in fetched_transcript:
        print(snippet.text)
