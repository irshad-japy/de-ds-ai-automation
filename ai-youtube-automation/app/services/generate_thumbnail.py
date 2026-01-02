"""
python -m app.services.generate_thumbnail
"""

import datetime as dt
import hashlib
import json
import re, os
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

KEYWORD_VISUALS = {
    "n8n": "a flat icon of connected workflow nodes (3-5 circles with lines), automation symbol",
    "youtube": "a simple red play button inside a rounded rectangle, flat icon style",
    "database": "a database cylinder icon, flat design",
    "sql": "a database cylinder with small query brackets, flat icon",
    "postgres": "a database cylinder icon, flat design",
    "mysql": "a database cylinder icon, flat design",
    "redis": "a stacked cache blocks icon, flat design",
    "fastapi": "a minimal API endpoint icon (brackets + lightning), flat design",
    "api": "a minimal API endpoint icon (brackets), flat design",
    "aws": "a cloud icon with small nodes, flat design",
    "lambda": "a minimal serverless lightning icon, flat design",
    "docker": "a container box icon, flat design",
    "kubernetes": "a cluster nodes hexagon-like symbol, flat design",
    "qdrant": "a vector dots cluster icon, flat design",
    "vector": "a vector dots cluster icon, flat design",
    "rag": "a magnifier over documents icon, flat design",
    "ai": "a brain/circuit icon, flat design",
    "agent": "a robot head icon, flat design",
}

def extract_visual_concepts(script: str, max_items: int = 3) -> list[str]:
    """
    Find relevant concepts in the script and return up to max_items visual concepts.
    """
    text = script.lower()

    found = []
    # Prefer important keywords first (stable ordering)
    for key in KEYWORD_VISUALS.keys():
        if re.search(rf"\b{re.escape(key)}\b", text):
            found.append(KEYWORD_VISUALS[key])

    # Fallback: always include something meaningful
    if not found:
        found = [
            "a flat icon of connected workflow nodes, automation symbol",
            "a simple red play button icon, flat design",
        ]

    # De-dup while preserving order
    uniq = []
    for x in found:
        if x not in uniq:
            uniq.append(x)

    return uniq[:max_items]

ICON_LIBRARY = {
    "n8n": Path("assets/icons/n8n.png"),
    "youtube": Path("assets/icons/youtube.png"),
    "database": Path("assets/icons/database.png"),
    "sql": Path("assets/icons/database.png"),
    "postgres": Path("assets/icons/database.png"),
    "mysql": Path("assets/icons/database.png"),
    "redis": Path("assets/icons/redis.png"),
    "fastapi": Path("assets/icons/api.png"),
    "api": Path("assets/icons/api.png"),
    "aws": Path("assets/icons/aws.png"),
    "lambda": Path("assets/icons/lambda.png"),
}

def extract_icon_keys(script: str, max_icons: int = 2) -> list[str]:
    text = script.lower()
    keys = []
    for k in ICON_LIBRARY.keys():
        if re.search(rf"\b{re.escape(k)}\b", text):
            keys.append(k)

    # de-dup preserve order
    out = []
    for k in keys:
        if k not in out:
            out.append(k)

    return out[:max_icons]

def load_icon(key: str) -> Image.Image:
    p = ICON_LIBRARY.get(key)
    if not p or not p.exists():
        raise FileNotFoundError(f"Icon missing for '{key}': {p}")
    return Image.open(p).convert("RGBA")

def paste_icons_row(base: Image.Image, icons: list[Image.Image], box: tuple[int,int,int,int], gap: int = 12) -> Image.Image:
    """
    Paste 1..N icons in a row inside given box (x0,y0,x1,y1).
    """
    base_rgba = base.convert("RGBA")
    x0, y0, x1, y1 = box
    bw, bh = (x1 - x0), (y1 - y0)

    n = max(1, len(icons))
    slot_w = (bw - gap * (n - 1)) // n

    for i, icon in enumerate(icons):
        # fit icon into its slot
        ow, oh = icon.size
        scale = min(slot_w / ow, bh / oh)
        nw, nh = int(ow * scale), int(oh * scale)
        icon_r = icon.resize((nw, nh), Image.LANCZOS)

        sx0 = x0 + i * (slot_w + gap)
        px = sx0 + (slot_w - nw) // 2
        py = y0 + (bh - nh) // 2

        base_rgba.paste(icon_r, (px, py), icon_r)

    return base_rgba.convert("RGB")

def build_prompts(topic: str, script: str) -> dict:
    concepts = extract_visual_concepts(script, max_items=3)

    background_prompt = (
        f"Professional YouTube thumbnail background for: {topic}. "
        f"Include subtle elements of: {', '.join(concepts[:2])}. "
        "Clean, modern, high-contrast, minimal clutter, tech automation theme. "
        "Abstract workflow nodes and connectors, subtle glowing UI shapes. "
        "Left side visual interest, right side clean empty space for text. "
        "No words, no watermark, no brand logos."
    )

    # Icon becomes a SINGLE combined icon tile, based on script
    icon_prompt = (
        "A clean flat icon tile on WHITE background featuring: "
        + ", ".join(concepts[:2]) +
        ". Minimal, high contrast, vector style, no text, no watermark."
    )

    return {
        "background_prompt": background_prompt,
        "icon_prompt": icon_prompt,
    }

@cache_file("output/cache", namespace="thumbs", ext=".png", out_arg="out_path")
def generate_thumbnail_from_script(script: str, seed: int | None = None) -> Path:
    ensure_dirs() 
    font_path = ensure_font()

    # ✅ NEW: random seed if not provided
    if seed is None:
        seed = int.from_bytes(os.urandom(4), "big")

    topic = extract_title_or_topic(script)
    headline = make_headline(topic)
    prompts = build_prompts(topic, script)

    pipe = sdxl_pipe(MODEL_ID)

    bg = gen_image(pipe, prompts["background_prompt"], NEGATIVE_PROMPT, BG_SIZE, seed=seed + 10)

    bg = resize_to_1280x720(bg)

    icon_keys = extract_icon_keys(script, max_icons=2)  # pick 1-2 icons from script
    if not icon_keys:
        icon_keys = ["youtube"]  # or "n8n" or your brand default
    icons = [load_icon(k) for k in icon_keys]

    # paste 1 or 2 icons in the top-right box
    bg = paste_icons_row(bg, icons, box=(1060, 40, 1250, 200))

    final_img = draw_big_text(bg, headline, font_path)

    script_id = hashlib.md5(script.encode("utf-8", errors="ignore")).hexdigest()[:8]
    out_path = OUT_DIR / f"thumb_{script_id}_seed_{seed}.png"
    final_img.save(out_path)

    return out_path

# # Example local run
if __name__ == "__main__":
    start = time.time()
    demo_script = """Learn how to build a dynamic ETL pipeline v PySpark and a Docker-based MySQL databa This POC shows how to create a metadata-driven job runner that executes ETL tasks (CSV or SQL source) based on control table entries. We cover Spark setup, environment variables, JDBC integration, and error fixes.\n\n🔧 Tech stack: PySpark, MySQL, Docker, SQLAlchemy, Pandas\n💡 Use case: Automate ETL jobs dynamically using metadata
        """
    out_path = generate_thumbnail_from_script(demo_script)
    logger.info(f"✅ Saved: {out_path}")
    end = time.time()
    logger.info(f'total time to execute {end-start} second')
    