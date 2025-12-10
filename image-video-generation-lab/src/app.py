"""
python -m src.app
# or
python src/app.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr

from t2i.generate import generate_image
from meme.generate import meme_from_prompt, meme_from_upload
from shorts.generate import main as shorts_cli_main  # noqa: F401 (imported for packaging/entrypoints)

from utils.paths import IMAGES_DIR, MEMES_DIR, VIDEOS_DIR, AUDIO_DIR  # noqa: F401 (AUDIO_DIR may be used by voice module)
from utils.text import enhance_prompt  # noqa: F401 (optional use)

load_dotenv()

MODEL_OPTIONS = {
    "SD 2.1 (very fast generation)": "stabilityai/sd-turbo",
    "High-capacity model": "stabilityai/sdxl-turbo",
    "Stable Diffusion 3.5 Large / Large-Turbo": "stabilityai/stable-diffusion-3.5-large-turbo",
}

# =========================
# Image Tab (Text-to-Image)
# =========================
def ui_t2i(prompt, negative, width, height, steps, guidance, seed, model, enhance):
    try:
        path = generate_image(
            prompt=prompt,
            negative_prompt=negative or None,
            width=width,
            height=height,
            steps=steps,
            guidance=guidance,
            seed=int(seed) if seed else None,
            model_id=MODEL_OPTIONS.get(model, os.getenv("MODEL_ID", "stabilityai/sd-turbo")),
            enhance=enhance,
            out_dir=IMAGES_DIR,
        )
        return str(path), str(path)  # path for textbox + filepath for gr.Image
    except Exception as e:
        return f"ERROR: {e}", None

# =================
# Meme Tab Helpers
# =================
def ui_meme_use_prompt(bg_prompt, top, bottom, model):
    try:
        p = meme_from_prompt(
            bg_prompt,
            top,
            bottom,
            model_id=MODEL_OPTIONS.get(model, os.getenv("MODEL_ID", "stabilityai/sd-turbo")),model_id=model or os.getenv("MODEL_ID", "stabilityai/sd-turbo"),
        )
        return str(p), str(p)
    except Exception as e:
        return f"ERROR: {e}", None

def ui_meme_use_upload(upload, top, bottom):
    if upload is None:
        return "Please upload an image.", None
    try:
        p = meme_from_upload(Path(upload), top, bottom)
        return str(p), str(p)
    except Exception as e:
        return f"ERROR: {e}", None

# ===========================
# Shorts / Video Tab Helpers
# ===========================
def ui_shorts(script, slides, seconds, model, voice):
    import sys
    import io
    from shorts.generate import main as shorts_main
    from contextlib import redirect_stdout

    argv_bak = sys.argv
    try:
        sys.argv = [
            "shorts.generate",
            "--script",
            script,
            "--slides",
            str(slides),
            "--seconds",
            str(seconds),
            "--model",
            model,
        ]
        if voice:
            sys.argv += ["--voice", voice]

        buf = io.StringIO()
        with redirect_stdout(buf):
            shorts_main()
        console = buf.getvalue()
    finally:
        sys.argv = argv_bak

    # Find newest mp4/srt produced in VIDEOS_DIR
    mp4s = sorted(VIDEOS_DIR.glob("*.mp4"))
    srts = sorted(VIDEOS_DIR.glob("*.srt"))
    vid = mp4s[-1] if mp4s else None
    srt = srts[-1] if srts else None
    return console, (str(vid) if vid else ""), (str(srt) if srt else ""), (str(vid) if vid else None)

# ===============
# Voice / TTS API
# ===============
def _ui_tts(provider, text, voice_id, model_tts):
    from voice.tts import synthesize_elevenlabs, synthesize_parler, synthesize_pyttsx3
    try:
        if provider == "ElevenLabs (cloud)":
            mid = model_tts or "eleven_multilingual_v2"
            return_path = synthesize_elevenlabs(text=text, voice_id=(voice_id or None), model_id=mid)
        elif provider == "Local Parler-TTS":
            mid = model_tts or "parler-tts/parler-tts-mini-v1"
            if "parler-tts" not in mid.lower():  # user left an ElevenLabs id
                mid = "parler-tts/parler-tts-mini-v1"
            return_path = synthesize_parler(text=text, model_id=mid)
        else:
            return_path = synthesize_pyttsx3(text=text)
        return str(return_path), str(return_path)
    except Exception as e:
        return f"ERROR: {e}", None

def _canon_file_path(f):
    # Works with gr.Files across versions: try .name (temp path), then .path, else string
    return getattr(f, "name", None) or getattr(f, "path", None) or (f if isinstance(f, str) else None)

def _ui_clone(name, files):
    from voice.tts import clone_voice_elevenlabs
    try:
        files = files or []
        file_paths = [p for p in (_canon_file_path(f) for f in files) if p]
        if not file_paths:
            return "ERROR: No valid files received.", ""
        vid = clone_voice_elevenlabs(name=name, files=file_paths)
        return "Cloned successfully.", vid
    except Exception as e:
        return f"ERROR: {e}", ""

# ===============
# Gradio UI
# ===============
with gr.Blocks(title="Image & Video Generation Lab", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 Image & Video Generation Lab")
    gr.Markdown("Build images, memes, shorts, and speech — beginner-friendly, CPU-compatible.")

    with gr.Tabs():
        # ================
        # Text-to-Image
        # ================
        with gr.Tab("Text-to-Image"):
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(
                        label="Prompt",
                        value="a cinematic 8k photorealistic fox in a forest",
                    )
                    negative = gr.Textbox(label="Negative prompt (optional)", value="")
                    with gr.Row():
                        width = gr.Slider(256, 1024, value=768, step=64, label="Width")
                        height = gr.Slider(256, 1024, value=768, step=64, label="Height")
                    with gr.Row():
                        steps = gr.Slider(1, 30, value=4, step=1, label="Steps")
                        guidance = gr.Slider(
                            0.0, 10.0, value=0.0, step=0.5, label="Guidance"
                        )
                    with gr.Row():
                        seed = gr.Textbox(label="Seed (blank = random)", value="")
                        model = gr.Dropdown(
                            label="Select Model",
                            choices=list(MODEL_OPTIONS.keys()),
                            value="SD 2.1 (very fast generation)",  # default label
                        )
                    enhance = gr.Checkbox(
                        label="Enhance with cinematic/8k keywords", value=True
                    )
                    btn_img = gr.Button("Generate Image")
                with gr.Column():
                    t2i_out_path = gr.Textbox(label="Saved path")
                    t2i_out_img = gr.Image(label="Result", interactive=False)

            btn_img.click(
                ui_t2i,
                [prompt, negative, width, height, steps, guidance, seed, model, enhance],
                [t2i_out_path, t2i_out_img],
            )

        # ===========
        # Meme Tab
        # ===========
        with gr.Tab("AI Meme Generator"):
            with gr.Row():
                with gr.Column():
                    bg_prompt = gr.Textbox(
                        label="(Option A) Background Prompt",
                        value="dramatic sunset over mountains",
                    )
                    top = gr.Textbox(label="Top Text", value="WHEN PROD WORKS")
                    bottom = gr.Textbox(label="Bottom Text", value="AND YOU DID NOTHING")
                    model2 = gr.Dropdown(
                        label="Select Model",
                        choices=list(MODEL_OPTIONS.keys()),
                        value="SD 2.1 (very fast generation)",
                    )
                    btn_meme_a = gr.Button("Create Meme from Prompt")
                with gr.Column():
                    upload = gr.Image(
                        type="filepath", label="(Option B) Or Upload Base Image"
                    )
                    btn_meme_b = gr.Button("Create Meme from Upload")
                    meme_path = gr.Textbox(label="Saved path")
                    meme_img = gr.Image(label="Meme", interactive=False)

            btn_meme_a.click(
                ui_meme_use_prompt, [bg_prompt, top, bottom, model2], [meme_path, meme_img]
            )
            btn_meme_b.click(
                ui_meme_use_upload, [upload, top, bottom], [meme_path, meme_img]
            )

        # ===================
        # Shorts / Video Tab
        # ===================
        with gr.Tab("AI Shorts / Video Generator"):
            with gr.Row():
                with gr.Column():
                    script = gr.Textbox(
                        label="Narration Script",
                        lines=6,
                        value="AI will transform workflows. Automate boring tasks. Focus on impact.",
                    )
                    slides = gr.Slider(3, 12, value=5, step=1, label="Slides (images)")
                    seconds = gr.Slider(2, 8, value=3, step=1, label="Seconds per slide")
                    model3 = gr.Dropdown(
                        label="Select Model",
                        choices=list(MODEL_OPTIONS.keys()),
                        value="SD 2.1 (very fast generation)",
                    )
                    voice = gr.Textbox(
                        label="ElevenLabs Voice ID (optional; uses .env default if blank)"
                    )
                    btn_video = gr.Button("Create Short Video")
                with gr.Column():
                    console = gr.Textbox(label="Build Log", lines=12)
                    mp4_path = gr.Textbox(label="MP4 path")
                    srt_path = gr.Textbox(label="SRT path")
                    vid = gr.Video(label="Preview (no burned captions)")

            btn_video.click(
                ui_shorts, [script, slides, seconds, model3, voice], [console, mp4_path, srt_path, vid]
            )

        # =============
        # Voice / TTS
        # =============
        with gr.Tab("Voice / TTS"):
            gr.Markdown(
                "### Text → Speech (Default: ElevenLabs). Optionally clone a voice and synthesize."
            )

            with gr.Row():
                with gr.Column():
                    provider = gr.Radio(
                        choices=[
                            "ElevenLabs (cloud)",
                            "Local Parler-TTS",
                            "Offline pyttsx3",
                        ],
                        value="ElevenLabs (cloud)",
                        label="Provider",
                    )
                    text = gr.Textbox(
                        label="Text to speak",
                        value="Hello, this is a test of the new voice tab!",
                        lines=4,
                    )
                    voice_id = gr.Textbox(
                        label="Voice ID (for ElevenLabs; optional)",
                        value=os.getenv("ELEVENLABS_DEFAULT_VOICE_ID", ""),
                    )
                    model_tts = gr.Textbox(
                        label="Model ID (ElevenLabs or Parler)",
                        value=os.getenv("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2"),
                    )
                    def _on_provider_change(p):
                        if p == "Local Parler-TTS":
                            return "parler-tts/parler-tts-mini-v1"
                        if p == "ElevenLabs (cloud)":
                            return "eleven_multilingual_v2"
                        # Offline pyttsx3 doesn't need a model id
                        return ""

                    def _toggle_voice_id(p):
                        # Voice ID only applies to ElevenLabs
                        return gr.update(interactive=(p == "ElevenLabs (cloud)"))

                    provider.change(_on_provider_change, inputs=provider, outputs=model_tts)
                    provider.change(_toggle_voice_id, inputs=provider, outputs=voice_id)
                    btn_tts = gr.Button("Synthesize")

                with gr.Column():
                    tts_out_path = gr.Textbox(label="Saved audio path")
                    tts_out_audio = gr.Audio(label="Preview", type="filepath")

            with gr.Accordion("Voice Cloning (ElevenLabs)", open=False):
                gr.Markdown(
                    "Upload a few clean voice samples (15–60 sec each). "
                    "This will create a new custom voice in your ElevenLabs account."
                )
                with gr.Row():
                    with gr.Column():
                        clone_name = gr.Textbox(label="Voice Name", value="MyClonedVoice")
                        clone_files = gr.Files(
                            label="Upload 1–5 sample audio files",
                            file_count="multiple",
                            type="filepath",
                        )
                        btn_clone = gr.Button("Create / Clone Voice")
                    with gr.Column():
                        clone_status = gr.Textbox(label="Clone status")
                        clone_voice_id = gr.Textbox(label="New Voice ID")

            # Wire Voice events
            btn_tts.click(
                _ui_tts, [provider, text, voice_id, model_tts], [tts_out_path, tts_out_audio]
            )
            btn_clone.click(
                _ui_clone, [clone_name, clone_files], [clone_status, clone_voice_id]
            )

if __name__ == "__main__":
    demo.launch()
