"""
python .\test\extract_video_scenes.py
"""

import os
import cv2
import pandas as pd
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.scene_manager import save_images
from pytubefix import YouTube
import subprocess

# ------------------------------------------------------------
# 1️⃣ Download YouTube video
# ------------------------------------------------------------
def clean_youtube_url(url: str) -> str:
    return url.split("?")[0]

def sanitize_folder_name(name: str) -> str:
    """Keep only alphanumeric & underscore-safe folder name."""
    return "".join(c if c.isalnum() or c in ("_", " ") else "" for c in name).strip()

def download_video(youtube_url, base_output="test/output"):
    yt = YouTube(youtube_url)
    title_words = yt.title.split()[:2]  # first two words
    title_prefix = sanitize_folder_name("_".join(title_words))
    
    video_base_dir = os.path.join(base_output, title_prefix)
    download_dir = os.path.join(video_base_dir, "downloads")
    scene_dir = os.path.join(video_base_dir, "scene_output")

    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(scene_dir, exist_ok=True)

    print(f"📁 Using base directory: {video_base_dir}")

    stream = yt.streams.filter(file_extension='mp4', progressive=True).get_highest_resolution()
    out_path = stream.download(download_dir)
    print(f"✅ Downloaded: {out_path}")
    return out_path, scene_dir

# ------------------------------------------------------------
# 2️⃣ Detect scenes dynamically (based on content)
# ------------------------------------------------------------
def detect_scenes(video_path, output_dir="test/output/scene_output", threshold=25.0, save_clips=True):
    os.makedirs(output_dir, exist_ok=True)
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))  # lower threshold = more cuts

    video_manager.set_downscale_factor()
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()

    print(f"🎞️ Detected {len(scene_list)} real scenes in video.")

    # Save scene thumbnails
    thumbnail_dir = os.path.join(output_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    save_images(scene_list, video_manager, num_images=1, output_dir=thumbnail_dir)

    # Save metadata
    scene_data = []
    for i, (start, end) in enumerate(scene_list):
        start_time = start.get_seconds()
        end_time = end.get_seconds()
        duration = round(end_time - start_time, 2)
        scene_thumb = os.path.join(thumbnail_dir, f"scene_{i+1:03d}.jpg")
        scene_clip = os.path.join(output_dir, f"scene_{i+1:03d}.mp4")

        scene_data.append({
            "scene_number": i + 1,
            "start_time_sec": start_time,
            "end_time_sec": end_time,
            "duration_sec": duration,
            "thumbnail": scene_thumb,
            "clip": scene_clip if save_clips else None
        })

        # Optionally cut scene clips (fast copy)
        if save_clips:
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-ss", str(start_time), "-to", str(end_time),
                "-c", "copy", scene_clip
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    video_manager.release()

    df = pd.DataFrame(scene_data)
    df.to_csv(os.path.join(output_dir, "scene_metadata.csv"), index=False)
    print(f"✅ Scene metadata saved: {len(df)} scenes detected.")
    return df


# ------------------------------------------------------------
# 3️⃣ Main Entry
# ------------------------------------------------------------
if __name__ == "__main__":
    url = input("Enter YouTube video URL: ").strip()
    clean_url = clean_youtube_url(url)
    video_path, output_dir = download_video(clean_url)
    detect_scenes(video_path, output_dir=output_dir, threshold=25.0, save_clips=True)
