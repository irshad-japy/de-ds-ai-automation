"""
python -m src.app
# or
python src/app.py
"""

import os, time
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr

from t2i.generate import generate_image
from meme.generate import meme_from_prompt, meme_from_upload
from shorts.generate import main as shorts_cli_main

from utils.paths import IMAGES_DIR, MEMES_DIR, VIDEOS_DIR, AUDIO_DIR
from utils.text import enhance_prompt

load_dotenv()

def ui_t2i(prompt, negative, width, height, steps, guidance, seed, model, enhance):
    try:
        path = generate_image(
            prompt=prompt,
            negative_prompt=negative or None,
            width=width, height=height,
            steps=steps, guidance=guidance,
            seed=int(seed) if seed else None,
            model_id=model or os.getenv("MODEL_ID", "stabilityai/sd-turbo"),
            enhance=enhance,
            out_dir=IMAGES_DIR,
        )
        return str(path), path
    except Exception as e:
        return f"ERROR: {e}", None

def ui_meme_use_prompt(bg_prompt, top, bottom, model):
    try:
        p = meme_from_prompt(bg_prompt, top, bottom, model_id=model or os.getenv("MODEL_ID", "stabilityai/sd-turbo"))
        return str(p), p
    except Exception as e:
        return f"ERROR: {e}", None

def ui_meme_use_upload(upload, top, bottom):
    if upload is None:
        return "Please upload an image.", None
    try:
        p = meme_from_upload(Path(upload), top, bottom)
        return str(p), p
    except Exception as e:
        return f"ERROR: {e}", None

def ui_shorts(script, slides, seconds, model, voice):
    # Call the CLI main under the hood; capture prints
    import sys, io
    from shorts.generate import main as shorts_main
    argv_bak = sys.argv
    try:
        sys.argv = ["shorts.generate", "--script", script, "--slides", str(slides), "--seconds", str(seconds), "--model", model]
        if voice:
            sys.argv += ["--voice", voice]
        buf = io.StringIO()
        from contextlib import redirect_stdout
        with redirect_stdout(buf):
            shorts_main()
        console = buf.getvalue()
    finally:
        sys.argv = argv_bak
    # Try to find the newest mp4 & srt
    mp4s = sorted(VIDEOS_DIR.glob("*.mp4"))
    srts = sorted(VIDEOS_DIR.glob("*.srt"))
    vid = mp4s[-1] if mp4s else None
    srt = srts[-1] if srts else None
    return console, (str(vid) if vid else ""), (str(srt) if srt else ""), (vid if vid else None)

with gr.Blocks(title="Image & Video Generation Lab", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 Image & Video Generation Lab")
    gr.Markdown("Build images, memes, and shorts — beginner‑friendly, CPU‑compatible.")

    with gr.Tab("Text‑to‑Image"):
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(label="Prompt", value="a cinematic 8k photorealistic fox in a forest")
                negative = gr.Textbox(label="Negative prompt (optional)", value="")
                with gr.Row():
                    width = gr.Slider(256, 1024, value=768, step=64, label="Width")
                    height = gr.Slider(256, 1024, value=768, step=64, label="Height")
                with gr.Row():
                    steps = gr.Slider(1, 30, value=4, step=1, label="Steps")
                    guidance = gr.Slider(0.0, 10.0, value=0.0, step=0.5, label="Guidance")
                with gr.Row():
                    seed = gr.Textbox(label="Seed (blank = random)", value="")
                    model = gr.Textbox(label="Model ID", value=os.getenv("MODEL_ID", "stabilityai/sd-turbo"))
                enhance = gr.Checkbox(label="Enhance with cinematic/8k keywords", value=True)
                btn = gr.Button("Generate Image")
            with gr.Column():
                out_path = gr.Textbox(label="Saved path")
                out_img = gr.Image(label="Result", interactive=False)

        btn.click(ui_t2i, [prompt, negative, width, height, steps, guidance, seed, model, enhance], [out_path, out_img])

    with gr.Tab("AI Meme Generator"):
        with gr.Row():
            with gr.Column():
                bg_prompt = gr.Textbox(label="(Option A) Background Prompt", value="dramatic sunset over mountains")
                top = gr.Textbox(label="Top Text", value="WHEN PROD WORKS")
                bottom = gr.Textbox(label="Bottom Text", value="AND YOU DID NOTHING")
                model2 = gr.Textbox(label="Model ID", value=os.getenv("MODEL_ID", "stabilityai/sd-turbo"))
                btnA = gr.Button("Create Meme from Prompt")
            with gr.Column():
                upload = gr.Image(type="filepath", label="(Option B) Or Upload Base Image")
                btnB = gr.Button("Create Meme from Upload")
                meme_path = gr.Textbox(label="Saved path")
                meme_img = gr.Image(label="Meme", interactive=False)

        btnA.click(ui_meme_use_prompt, [bg_prompt, top, bottom, model2], [meme_path, meme_img])
        btnB.click(ui_meme_use_upload, [upload, top, bottom], [meme_path, meme_img])

    with gr.Tab("AI Shorts / Video Generator"):
        with gr.Row():
            with gr.Column():
                script = gr.Textbox(label="Narration Script", lines=6, value="AI will transform workflows. Automate boring tasks. Focus on impact.")
                slides = gr.Slider(3, 12, value=5, step=1, label="Slides (images)")
                seconds = gr.Slider(2, 8, value=3, step=1, label="Seconds per slide")
                model3 = gr.Textbox(label="Model ID", value=os.getenv("MODEL_ID", "stabilityai/sd-turbo"))
                voice = gr.Textbox(label="ElevenLabs Voice ID (optional; uses .env default if blank)")
                btnV = gr.Button("Create Short Video")
            with gr.Column():
                console = gr.Textbox(label="Build Log", lines=12)
                mp4_path = gr.Textbox(label="MP4 path")
                srt_path = gr.Textbox(label="SRT path")
                vid = gr.Video(label="Preview (no burned captions)")
        btnV.click(ui_shorts, [script, slides, seconds, model3, voice], [console, mp4_path, srt_path, vid])

if __name__ == "__main__":
    demo.launch()
