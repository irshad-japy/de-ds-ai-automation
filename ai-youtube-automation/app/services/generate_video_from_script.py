import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# -------------------------------------------------------
# Load API key from .env
# -------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("LTX_API_KEY")
if not API_KEY:
    raise ValueError("⚠️  Missing LTX_API_KEY in .env file")

# -------------------------------------------------------
# User-defined inputs
# -------------------------------------------------------
SCRIPT_FILE = "input_script.txt"     # your text script file
MODEL = "ltx-2-pro"                 # free-tier model works too (auto-downgraded if needed)
DURATION = 8                        # in seconds
RESOLUTION = "1280x720"             # 720p is faster; use 1920x1080 for HD
OUTPUT_FILE = "generated_video.mp4" # local output
API_URL = "https://api.ltx.video/v1/text-to-video"

# -------------------------------------------------------
# Read your text script
# -------------------------------------------------------
if not Path(SCRIPT_FILE).exists():
    raise FileNotFoundError(f"{SCRIPT_FILE} not found")

with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
    text_prompt = f.read().strip()

print(f"[INFO] Prompt loaded ({len(text_prompt)} chars)")

# -------------------------------------------------------
# Build payload
# -------------------------------------------------------
payload = {
    "prompt": text_prompt,
    "model": MODEL,
    "duration": DURATION,
    "resolution": RESOLUTION
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# -------------------------------------------------------
# Send request
# -------------------------------------------------------
print("[INFO] Sending request to LTX Video API...")
response = requests.post(API_URL, json=payload, headers=headers)

# -------------------------------------------------------
# Handle response
# -------------------------------------------------------
if response.status_code == 200:
    Path(OUTPUT_FILE).write_bytes(response.content)
    print(f"[✅] Video saved successfully → {OUTPUT_FILE}")
else:
    print(f"[❌] Request failed (status {response.status_code})")
    try:
        print("Error details:", response.json())
    except Exception:
        print("Response preview:", response.text[:500])
