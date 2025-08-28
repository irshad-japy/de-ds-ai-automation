import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
IMAGES_DIR = OUTPUTS / "images"
MEMES_DIR = OUTPUTS / "memes"
VIDEOS_DIR = OUTPUTS / "videos"
AUDIO_DIR = OUTPUTS / "audio"

for p in [IMAGES_DIR, MEMES_DIR, VIDEOS_DIR, AUDIO_DIR]:
    p.mkdir(parents=True, exist_ok=True)
