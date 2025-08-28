

import argparse, os, time, math
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

from t2i.generate import generate_image
from utils.paths import VIDEOS_DIR, AUDIO_DIR
from utils.text import split_into_sentences
from utils.audio import tts_offline_to_wav, tts_elevenlabs_to_wav
from subtitles.build_srt import build_even_srt
from subtitles.whisper_optional import transcribe_with_whisper

def make_slideshow(images: List[Path], audio_path: Path, seconds_per_slide: int, out_path: Path) -> Path:
    
    audio = AudioFileClip(str(audio_path))
    clips = []
    for img in images:
        ic = ImageClip(str(img)).with_duration(seconds_per_slide)
        clips.append(ic)
    video = concatenate_videoclips(clips, method="compose").with_audio(audio)
    # Match video duration to audio
    if video.duration > audio.duration:
        video = video.subclipped(0, audio.duration)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(
        str(out_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",   # very fast encoding
        bitrate="1000k"       # lower quality but much faster
    )
    audio.close()
    return out_path

def script_to_keyprompts(script: str, slides: int) -> List[str]:
    # naive split + padding
    sents = split_into_sentences(script)
    if not sents:
        sents = [script] if script.strip() else ["AI generated visual"]
    if len(sents) >= slides:
        return sents[:slides]
    # pad by repeating
    out = []
    i = 0
    while len(out) < slides:
        out.append(sents[i % len(sents)])
        i += 1
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="Narration text")
    ap.add_argument("--slides", type=int, default=5, help="Number of images")
    ap.add_argument("--seconds", type=int, default=3, help="Seconds per slide")
    ap.add_argument("--model", default="stabilityai/sd-turbo", help="Diffusers model id")
    ap.add_argument("--voice", default=None, help="ElevenLabs voice id (optional if using ElevenLabs)")
    args = ap.parse_args()

    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY") or ""
    default_voice = os.getenv("ELEVENLABS_VOICE_ID", "Rachel")
    model_id = os.getenv("MODEL_ID", args.model)
    use_whisper = (os.getenv("USE_WHISPER", "false").lower() == "true")

    # 1) Generate key prompts for visuals
    keyprompts = script_to_keyprompts(args.script, args.slides)

    # 2) Generate images
    img_paths = []
    for kp in keyprompts:
        img = generate_image(kp, model_id=model_id, steps=4, guidance=0.0, width=768, height=768)
        img_paths.append(img)

    # 3) TTS
    ts = time.strftime("%Y%m%d_%H%M%S")
    audio_path = AUDIO_DIR / f"narration_{ts}.wav"
    if api_key:
        voice = args.voice or default_voice or "Rachel"
        audio_path = tts_elevenlabs_to_wav(args.script, api_key, voice, audio_path)
    else:
        audio_path = tts_offline_to_wav(args.script, audio_path)

    # 4) Build captions
    srt_text = None
    if use_whisper:
        srt_text = transcribe_with_whisper(audio_path)
    if not srt_text:
        # fallback: even split
        
        dur = AudioFileClip(str(audio_path)).duration
        from ..utils.text import split_into_sentences
        srt_text = build_even_srt(split_into_sentences(args.script), dur)

    srt_path = VIDEOS_DIR / f"short_{ts}.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_text)

    # 5) Compose slideshow video with sidecar SRT
    video_path = VIDEOS_DIR / f"short_{ts}.mp4"
    video_path = make_slideshow(img_paths, audio_path, args.seconds, video_path)

    print(str(video_path))
    print(str(srt_path))
    print("Done. Your MP4 is ready; the SRT captions are next to it.")
    print("To burn captions into video (optional), you can use an ffmpeg command like:")
    print(f'ffmpeg -i "{video_path}" -i "{srt_path}" -c:v libx264 -c:a copy -vf subtitles="{srt_path}" "{video_path.with_name(video_path.stem + "_subtitled.mp4")}"')


if __name__ == "__main__":
    main()
