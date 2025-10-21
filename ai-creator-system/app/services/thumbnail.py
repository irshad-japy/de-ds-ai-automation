from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from ..utils.io import ensure_dir

DEFAULT_SIZE = (1920, 1080)

def create_thumbnail(title: str, subtitle: str, branding: str, style: str, out_path: Path) -> Path:
    out_path = ensure_dir(out_path, 'thumbnail.png')
    img = Image.new("RGB", DEFAULT_SIZE, (20, 20, 20))
    draw = ImageDraw.Draw(img)

    # Basic font fallbacks
    try:
        font_title = ImageFont.truetype("arial.ttf", 120)
        font_sub = ImageFont.truetype("arial.ttf", 64)
        font_brand = ImageFont.truetype("arial.ttf", 48)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # Title
    draw.text((100, 350), title, fill=(255, 255, 255), font=font_title)
    draw.text((100, 500), subtitle, fill=(220, 220, 220), font=font_sub)
    draw.text((100, 950), branding, fill=(180, 180, 180), font=font_brand)

    img.save(out_path)
    return out_path 