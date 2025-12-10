import argparse, time, os
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from t2i.generate import generate_image
from utils.paths import MEMES_DIR

def find_font():
    # Try common Impact locations or fallback to default PIL font
    candidates = [
        "/usr/share/fonts/truetype/impact.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/Impact.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, 48)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_text_with_outline(draw, pos, text, font, fill="white", outline="black", stroke=3):
    draw.text(pos, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=outline, align="center", anchor="mm")

def create_meme(
    base_img: Image.Image,
    top_text: str = "",
    bottom_text: str = "",
) -> Image.Image:
    W, H = base_img.size
    font_size = max(24, int(W * 0.06))
    font = find_font()
    try:
        font = ImageFont.truetype(font.path if hasattr(font, "path") else "arial.ttf", font_size)
    except Exception:
        # Fallback to default size scaling by repeatedly trying
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    draw = ImageDraw.Draw(base_img)
    if top_text:
        draw_text_with_outline(draw, (W/2, H*0.08), top_text.upper(), font)
    if bottom_text:
        draw_text_with_outline(draw, (W/2, H*0.92), bottom_text.upper(), font)
    return base_img

def meme_from_prompt(
    background_prompt: str,
    top: str,
    bottom: str,
    model_id: str = "stabilityai/sd-turbo",
    width: int = 768,
    height: int = 768,
    out_dir: Path = MEMES_DIR,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    bg_path = generate_image(background_prompt, model_id=model_id, width=width, height=height, steps=4, guidance=0.0)
    img = Image.open(bg_path).convert("RGB")
    meme = create_meme(img, top, bottom)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"meme_{ts}.png"
    meme.save(out_path)
    return out_path

def meme_from_upload(
    upload_path: Path,
    top: str,
    bottom: str,
    out_dir: Path = MEMES_DIR,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(upload_path).convert("RGB")
    meme = create_meme(img, top, bottom)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"meme_{ts}.png"
    meme.save(out_path)
    return out_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--background-prompt", default=None, help="If set, generate a background via SD")
    ap.add_argument("--upload", default=None, help="Use an existing image path instead")
    ap.add_argument("--top", default="", help="Top text")
    ap.add_argument("--bottom", default="", help="Bottom text")
    ap.add_argument("--model", default="stabilityai/sd-turbo")
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--height", type=int, default=768)
    args = ap.parse_args()

    if args.background_prompt:
        out = meme_from_prompt(args.background_prompt, args.top, args.bottom, model_id=args.model, width=args.width, height=args.height)
    elif args.upload:
        out = meme_from_upload(Path(args.upload), args.top, args.bottom)
    else:
        raise SystemExit("Provide either --background-prompt or --upload")
    print(str(out))

if __name__ == "__main__":
    main()
