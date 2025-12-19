"""
python -m app.services.generate_thumbnail
"""

import datetime as dt
import hashlib
import json
import re
import time
from io import BytesIO
from pathlib import Path
import requests
import torch
import logging
from diffusers import StableDiffusionXLPipeline
from PIL import Image, ImageDraw, ImageFont
from app.utils.file_cache import cache_file
from app.utils.structured_logging import get_logger, log_message

logger = get_logger("generate_thumbnail", logging.DEBUG)

# Optional background removal (auto-enabled if installed)

rembg_remove = None

# -----------------------------
# Defaults
# -----------------------------
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
OUT_DIR = Path("output/thumbnail")
CACHE_DIR = Path(".thumb_cache")

NEGATIVE_PROMPT = (
    "blurry, low resolution, too much text, crowded, noisy background, "
    "distorted logos, extra fingers, watermark, grainy, jpeg artifacts, "
    "bad anatomy, deformed, disfigured, unreadable text, low contrast"
)

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf"
FONT_PATH = CACHE_DIR / "Anton-Regular.ttf"

BG_SIZE = (1344, 768)
SUBJECT_SIZE = (1024, 1024)
ICON_SIZE = (512, 512)

_PIPE = None  # cache pipeline for speed

def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def ensure_font() -> Path:
    ensure_dirs()
    if FONT_PATH.exists():
        return FONT_PATH
    r = requests.get(FONT_URL, timeout=60)
    r.raise_for_status()
    FONT_PATH.write_bytes(r.content)
    return FONT_PATH

def extract_title_or_topic(script: str) -> str:
    m = re.search(r"(?im)^\s*(title|topic)\s*:\s*(.+?)\s*$", script)
    if m:
        return m.group(2).strip()

    for line in script.splitlines():
        line = line.strip()
        if line and len(line) > 6:
            return line[:140].strip()

    return "YouTube Automation Tutorial"

def make_headline(topic: str) -> str:
    stop = {
        "the","a","an","and","or","to","for","of","in","on","with","using","from","by",
        "how","what","why","this","that","your","you","my","is","are","be"
    }
    words = re.findall(r"[A-Za-z0-9\+\-]+", topic)
    words = [w for w in words if w.lower() not in stop]

    priority = []
    for key in ["n8n", "youtube", "automation", "ai", "agent", "workflow", "fastapi", "aws"]:
        for w in words:
            if w.lower() == key:
                priority.append(w)

    merged = []
    for w in priority + words:
        if w.upper() not in [x.upper() for x in merged]:
            merged.append(w)

    headline = " ".join(merged[:4]).upper()
    if len(headline) < 8:
        headline = topic[:28].upper()
    return headline[:28].strip()

def sdxl_pipe(model_id: str = MODEL_ID) -> StableDiffusionXLPipeline:
    global _PIPE
    if _PIPE is not None:
        return _PIPE

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        use_safetensors=True,
        variant="fp16" if dtype == torch.float16 else None,
    ).to(device)

    try:
        pipe.enable_vae_slicing()
        pipe.enable_attention_slicing()
    except Exception:
        pass

    _PIPE = pipe
    return pipe

def gen_image(pipe: StableDiffusionXLPipeline, prompt: str, negative: str, size: tuple[int, int], seed: int,
              steps: int = 30, guidance: float = 6.0) -> Image.Image:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    g = torch.Generator(device=device).manual_seed(seed)
    w, h = size
    return pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=w,
        height=h,
        num_inference_steps=steps,
        guidance_scale=guidance,
        generator=g,
    ).images[0]

def center_crop_to_aspect(img: Image.Image, aspect_w=16, aspect_h=9) -> Image.Image:
    w, h = img.size
    target = aspect_w / aspect_h
    current = w / h
    if current > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(w / target)
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))

def resize_to_1280x720(img: Image.Image) -> Image.Image:
    img = center_crop_to_aspect(img, 16, 9)
    return img.resize((1280, 720), Image.LANCZOS)

def to_transparent_png(img: Image.Image) -> Image.Image:
    """Remove background using rembg, returning RGBA image."""
    rgba = img.convert("RGBA")

    if rembg_remove is None:
        return rgba

    # Encode to PNG bytes -> rembg -> decode
    buf = BytesIO()
    rgba.save(buf, format="PNG")
    in_bytes = buf.getvalue()

    out_bytes = rembg_remove(in_bytes)  # returns PNG bytes
    return Image.open(BytesIO(out_bytes)).convert("RGBA")

def paste_centered(base: Image.Image, overlay: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    base_rgba = base.convert("RGBA")
    overlay_rgba = overlay.convert("RGBA")

    x0, y0, x1, y1 = box
    bw, bh = (x1 - x0), (y1 - y0)

    ow, oh = overlay_rgba.size
    scale = min(bw / ow, bh / oh)
    nw, nh = int(ow * scale), int(oh * scale)
    overlay_rgba = overlay_rgba.resize((nw, nh), Image.LANCZOS)

    px = x0 + (bw - nw) // 2
    py = y0 + (bh - nh) // 2

    base_rgba.paste(overlay_rgba, (px, py), overlay_rgba)
    return base_rgba.convert("RGB")

def draw_big_text(base: Image.Image, text: str, font_path: Path) -> Image.Image:
    img = base.convert("RGBA")
    d = ImageDraw.Draw(img)
    W, H = img.size

    x0 = int(W * 0.53)
    y0 = int(H * 0.12)
    x1 = W - 40
    region_w = x1 - x0

    words = text.split()

    def wrap_for_font(font):
        cur = ""
        out = []
        for w in words:
            test = (cur + " " + w).strip()
            bbox = d.textbbox((0, 0), test, font=font, stroke_width=10)
            if (bbox[2] - bbox[0]) <= region_w:
                cur = test
            else:
                if cur:
                    out.append(cur)
                cur = w
        if cur:
            out.append(cur)
        return out[:3]

    chosen_font = None
    chosen_lines = None
    for fs in [120, 112, 104, 96, 88, 80, 72, 64]:
        font = ImageFont.truetype(str(font_path), fs)
        candidate = wrap_for_font(font)
        if all((d.textbbox((0, 0), ln, font=font, stroke_width=10)[2] <= region_w) for ln in candidate):
            chosen_font, chosen_lines = font, candidate
            break

    if chosen_font is None:
        chosen_font = ImageFont.truetype(str(font_path), 64)
        chosen_lines = wrap_for_font(chosen_font)

    y = y0
    for ln in chosen_lines:
        d.text(
            (x0, y),
            ln,
            font=chosen_font,
            fill=(255, 255, 255, 255),
            stroke_width=12,
            stroke_fill=(0, 0, 0, 255),
        )
        y += int(chosen_font.size * 1.12)

    return img.convert("RGB")

def build_prompts(topic: str) -> dict:
    background_prompt = (
        f"Professional YouTube thumbnail background for: {topic}. "
        "Clean, modern, high-contrast, minimal clutter, tech automation theme. "
        "Abstract workflow nodes and connectors, subtle glowing UI shapes. "
        "Composition: left side has visual interest, right side is clean empty space for text. "
        "No words, no watermark, no brand logos, sharp, cinematic lighting."
    )

    subject_prompt = (
        "A friendly 3D robot character, confident pose, clean WHITE background, "
        "studio lighting, ultra sharp, high quality, no text, no watermark."
    )

    icon_prompt = (
        "A simple red play-button icon, flat design, clean WHITE background, "
        "high contrast, no text, no watermark."
    )

    return {
        "background_prompt": background_prompt,
        "subject_prompt": subject_prompt,
        "icon_prompt": icon_prompt,
    }

@cache_file("output/cache", namespace="thumbs", ext=".png", out_arg="out_path")
def generate_thumbnail_from_script(script: str, seed: int = 42) -> Path:
    """
    Single entry point: only script text in, thumbnail path out.
    """
    ensure_dirs()
    font_path = ensure_font()

    topic = extract_title_or_topic(script)
    headline = make_headline(topic)
    prompts = build_prompts(topic)

    pipe = sdxl_pipe(MODEL_ID)

    bg = gen_image(pipe, prompts["background_prompt"], NEGATIVE_PROMPT, BG_SIZE, seed=seed + 10)
    subject = gen_image(pipe, prompts["subject_prompt"], NEGATIVE_PROMPT, SUBJECT_SIZE, seed=seed + 20)
    icon = gen_image(pipe, prompts["icon_prompt"], NEGATIVE_PROMPT, ICON_SIZE, seed=seed + 30)

    bg = resize_to_1280x720(bg)

    subject_rgba = to_transparent_png(subject)
    icon_rgba = to_transparent_png(icon)

    bg = paste_centered(bg, subject_rgba, box=(20, 80, 610, 700))
    bg = paste_centered(bg, icon_rgba, box=(1080, 40, 1240, 200))

    final_img = draw_big_text(bg, headline, font_path)

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    script_id = hashlib.md5(script.encode("utf-8", errors="ignore")).hexdigest()[:8]

    out_path = OUT_DIR / f"thumb_{ts}_{script_id}.png"
    final_img.save(out_path)

    return out_path

# # Example local run
# if __name__ == "__main__":
#     start = time.time()
#     demo_script = "Have you ever wanted to give an AI agent access to your own private research documents without uploading everything to the cloud or paying huge API fees? Imagine typing a question into Claude Desktop, but instead of just relying on its training data, it instantly pulls answers from your local database running on your own machine. That is exactly what we are building today. We are going to create a custom Model Context Protocol, or MCP server, using FastAPI, connect it to a local Qdrant vector database, and power the whole thing with Ollama. This is a massive step forward for anyone interested in deep research automation and local AI privacy. Welcome back to Qubot AI Automation. If you are a busy creator or developer looking to streamline your workflow, you are in the right place. Today, we are tackling a Proof of Concept that connects several powerful tools. We are moving beyond simple scripts and building a robust architecture that acts as the brain for your automation projects. I know a lot of you have been hearing about MCP servers recently. It feels like the new standard for connecting AI tools, and frankly, it is. But the documentation can be a bit heavy. So, I spent the last few days banging my head against the wall to figure out the simplest way to get this running, so you don't have to. Let's start with the Why. Why build this specific stack? We have FastAPI as our backbone. It is fast, lightweight, and perfect for building the endpoints that the MCP protocol needs. Then we have Ollama. This allows us to run models like Llama 3 or Mistral locally. This is crucial for embedding our data—transforming text into numbers that the computer understands—without paying OpenAI for embeddings. Finally, we use Qdrant. Qdrant is a fantastic vector search engine. It stores those embeddings and lets us find relevant information in milliseconds. By combining these, you get a research agent that lives entirely on your laptop Here is the first hurdle I faced during this research. When you look at the MCP documentation, most examples use standard input and output, or stdio. That works great for simple command-line tools. But if you want to integrate this with n8n later, or if you want to debug what is actually happening, running an HTTP server with Server-Sent Events, or SSE, is much better. So, that is the route we are taking today. We are building an SSE-based MCP server"
#     out_path = generate_thumbnail_from_script(demo_script, seed=42)
#     logger.info(f"✅ Saved: {out_path}")
#     end = time.time()
#     logger.info(f'total to to execute {end-start} second')