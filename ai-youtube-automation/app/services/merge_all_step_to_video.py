"""
python -m app.services.merge_all_step_to_video
"""

from __future__ import annotations
from pathlib import Path
import logging
from app.utils.file_cache import cache_file
from app.services.voice_to_video_merge import merge_voice_and_video
from app.services.merge_hooks_video import merge_hook_full_video
from app.services.merge_thumbnail_video import add_image_invideo
from app.services.add_bg_music_on_video import add_background_music
from app.services.append_video_tail import append_video_to_end

from app.utils.structured_logging import get_logger, log_message
logger = get_logger("merge_all_step_to_video", logging.DEBUG)

OUT_DIR = Path("output/merge_video")

@cache_file("output/cache", namespace="video", ext=".mp4", out_arg="out_path")
def merge_main(
    full_video_path: str | Path,
    full_audio_path: str | Path,
    cut_mode: str,
    hook_audio: str | Path,
    hook_video: str | Path,
    thumbnail_path: str | Path,
    music_path: str | Path,
) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    full_video_path = Path(full_video_path)
    full_audio_path = Path(full_audio_path)
    hook_audio = Path(hook_audio)
    hook_video = Path(hook_video)
    thumbnail_path = Path(thumbnail_path)
    music_path = Path(music_path)
    end_video = "assets/video/demo_video.mp4"
    disclaimer_path = "assets/image/demo_disclaimer.png"

    merged_hook_video = merge_voice_and_video(hook_video, hook_audio, cut_mode)
    merged_full_video = merge_voice_and_video(full_video_path, full_audio_path, cut_mode)

    video_with_disclaimer = add_image_invideo(merged_full_video, disclaimer_path, intro_second=5) # add disclaimer in start before merge hooks

    merged_with_hook = merge_hook_full_video(merged_hook_video, video_with_disclaimer)
    merged_with_thumb = add_image_invideo(merged_with_hook, thumbnail_path)

    video_with_bg_music = add_background_music(merged_with_thumb, music_path)
    merged_final = append_video_to_end(video_with_bg_music, end_video)

    logger.info(f'final full merge video {merged_final}')
    
    return Path(merged_final)

if __name__ == "__main__":
    
    Full_video_path = "output/merge_video/demo_video_merged.mp4"
    Full_audio_path = "output/clone_voice/deepak_en.wav"
    cut_mode = "None"
    hook_audio = "output/clone_voice/deepak_en.wav"
    hook_video = "output/hooks/hook_15s.mp4"
    thumbnail_path = "assets/image/thumbnail_path.png"
    music_path = "assets/audio/background-music-159125.mp3"

    out = merge_main(Full_video_path, Full_audio_path, cut_mode, hook_audio, hook_video, thumbnail_path, music_path)
    logger.info(f"✅ Saved: {out.resolve()}")
