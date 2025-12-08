from pydub import AudioSegment
from pathlib import Path
from ..utils.io import ensure_dir

# Requires ffmpeg installed on system

def mix_with_bg(narration_path: Path, bg_music_path: Path, out_path: Path, bg_gain_db: float = -12.0) -> Path:
    narration = AudioSegment.from_file(narration_path)
    bg = AudioSegment.from_file(bg_music_path)

    # Loop bg to narration length
    while len(bg) < len(narration):
        bg += bg

    bg = bg - abs(bg_gain_db)
    mixed = bg.overlay(narration)

    out_path = ensure_dir(out_path, 'narration_mix.mp3')
    mixed.export(out_path, format="mp3")
    return out_path
