"""
Generate YouTube-style thumbnail from text content (offline)
"""

import os
import random
import nltk
from PIL import Image, ImageDraw, ImageFont

# Download tokenizer (only first time)
nltk.download("punkt", quiet=True)

# ===================================================
# ✅ Extract keywords or short title from text
# ===================================================
def extract_title_from_text(text: str, max_words: int = 6) -> str:
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return "My YouTube Video"
    # Take first sentence and shorten it
    title = sentences[0].strip().replace("\n", " ")
    return " ".join(title.split()[:max_words]).title()

# ===================================================
# ✅ Generate thumbnail from text
# ===================================================
def generate_thumbnail(script_path: str, output_path: str = "output/thumbnail.png"):
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if not text.strip():
        raise ValueError("File is empty — cannot generate thumbnail")

    # Extract short title
    title = extract_title_from_text(text)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Random bright background
    colors = [(255, 99, 71), (30, 144, 255), (255, 215, 0), (50, 205, 50), (186, 85, 211)]
    bg_color = random.choice(colors)

    # Create canvas 1280x720 (YouTube standard)
    img = Image.new("RGB", (1280, 720), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()

    # Text wrapping
    lines = []
    words = title.split()
    line = ""
    for word in words:
        if len(line + word) < 20:
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    # Center text on canvas
    total_height = len(lines) * 100
    y = (720 - total_height) // 2
    for line in lines:
        # ✅ Compute text width and height safely (compatible with Pillow ≥10)
        try:
            # Pillow ≥10
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            # Older Pillow
            w, h = draw.textsize(line, font=font)

        x = (1280 - w) // 2
        draw.text((x, y), line, fill="white", font=font, stroke_width=3, stroke_fill="black")
        y += h + 20

    # Save thumbnail
    img.save(output_path)
    print(f"✅ Thumbnail saved: {output_path}")
    return output_path

# ===================================================
# ✅ CLI entry point
# ===================================================
if __name__ == "__main__":
    script_path = "ai_youtube_video_bot/output/alarm_clock_story.txt"
    output_path = "ai_youtube_video_bot/output/thumbnail.png"
    generate_thumbnail(script_path, output_path)
