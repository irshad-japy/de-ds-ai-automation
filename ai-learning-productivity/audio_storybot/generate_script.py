
"""
generate_script.py
Standalone helper that:
1) Calls your running audio_storybot FastAPI `/explain` endpoint
2) Saves the returned script to .txt and .md
3) Optionally creates an MP3 via gTTS (if `--voice en` etc.)

Usage examples:
  python generate_script.py --file-path "C:\path\to\file.py" --mode story --language en --voice en
  python generate_script.py --file-url "https://raw.githubusercontent.com/user/repo/main/app.py" --mode script --voice en
  python generate_script.py --file-path ./demo.txt --mode story --voice en --audience Beginner --tone calm --humor 1 --seconds 90 --words 180 --analogy cricket

Requires:
  - Your FastAPI app running (e.g., `uvicorn app:app --host 0.0.0.0 --port 8099`)
  - pip install: requests, gTTS

Outputs are written to: ./output_script/
"""
import argparse, os, pathlib, time, requests, json, datetime
from typing import Optional
from gtts import gTTS

OUTPUT_DIR = pathlib.Path(os.getenv("OUTPUT_SCRIPT_DIR", "./output_script")).expanduser()
API_URL    = os.getenv("STORYBOT_URL", "http://localhost:8099/explain")  # change if you host elsewhere

def nowstamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def build_payload(args: argparse.Namespace) -> dict:
    controls = {
        "target_audience": args.audience,
        "tone": args.tone,
        "humor_level": args.humor,
        "reading_time_sec": args.seconds,
        "target_words": args.words,
        "analogy_domain": args.analogy,
        "language": args.language,
    }
    payload = {
        "mode": args.mode,
        "language": args.language,
        "controls": controls,
    }
    if args.file_path:
        payload["file_path"] = args.file_path
    if args.file_url:
        payload["file_url"] = args.file_url
    return payload

def main():
    parser = argparse.ArgumentParser(description="Generate script + optional audio using your running FastAPI.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--file-path", help="Local file path to analyze")
    src.add_argument("--file-url", help="Raw file URL to analyze")
    parser.add_argument("--mode", choices=["story","script"], default="story")
    parser.add_argument("--language", default="en")
    parser.add_argument("--audience", default="Beginner")
    parser.add_argument("--tone", default="calm")
    parser.add_argument("--humor", type=int, default=1)
    parser.add_argument("--seconds", type=int, default=90)
    parser.add_argument("--words", type=int, default=180)
    parser.add_argument("--analogy", default=None)
    parser.add_argument("--voice", default=None, help="gTTS voice code like 'en', 'en-uk', 'en-in'. If set, will synthesize MP3.")
    parser.add_argument("--title", default=None, help="Optional file base-name for outputs; else auto.")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = build_payload(args)
    try:
        res = requests.post(API_URL, json=payload, timeout=180)
    except Exception as e:
        print(f"[ERROR] Could not reach {API_URL}: {e}")
        print("Make sure your FastAPI is running. Example:\n  uvicorn app:app --host 0.0.0.0 --port 8099")
        return

    if res.status_code != 200:
        print(f"[ERROR] HTTP {res.status_code}: {res.text[:500]}")
        return

    data = res.json()
    # Expected: data has fields: 'story' or 'script', plus 'meta'
    text = data.get("story") or data.get("script") or json.dumps(data, indent=2)
    title = args.title or data.get("meta", {}).get("title") or f"script_{nowstamp()}"
    safe_title = "".join(ch for ch in title if ch.isalnum() or ch in ("-","_"," ")).rstrip().replace(" ", "_")

    txt_path = OUTPUT_DIR / f"{safe_title}.txt"
    md_path  = OUTPUT_DIR / f"{safe_title}.md"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Generated Script\n\n")
        f.write(text)

    print(f"[OK] Saved text -> {txt_path}")
    print(f"[OK] Saved markdown -> {md_path}")

    # Optional TTS
    if args.voice:
        try:
            tts = gTTS(text=text, lang=args.voice if args.voice != "en" else "en")
            mp3_path = OUTPUT_DIR / f"{safe_title}.mp3"
            tts.save(str(mp3_path))
            print(f"[OK] Saved audio -> {mp3_path}")
        except Exception as e:
            print(f"[WARN] Failed TTS: {e}")

if __name__ == "__main__":
    main()
