"""
python -m src.t2i.generate -p "cinematic 8k photorealistic portrait of a lion" -o outputs/images
"""

import argparse, os, time
from pathlib import Path
from typing import Optional

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image

from utils.paths import IMAGES_DIR
from utils.text import enhance_prompt

# IMAGES_DIR = os.path.join('outputs', 'images')


def get_pipe(model_id: str):
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = AutoPipelineForText2Image.from_pretrained(
        model_id,
        torch_dtype=dtype,
        variant="fp16" if torch.cuda.is_available() else None,
    )
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    else:
        pipe = pipe.to("cpu")
        pipe.enable_attention_slicing()
    return pipe

def generate_image(
    prompt: str,
    negative_prompt: Optional[str] = None,
    width: int = 768,
    height: int = 768,
    steps: int = 4,
    guidance: float = 0.0,
    seed: Optional[int] = None,
    model_id: str = "stabilityai/sd-turbo",
    enhance: bool = True,
    out_dir: Path = IMAGES_DIR,
) -> Path:
    prompt = enhance_prompt(prompt, enhance=enhance)
    out_dir.mkdir(parents=True, exist_ok=True)
    pipe = get_pipe(model_id)

    gen = torch.Generator(device=pipe.device).manual_seed(seed) if seed is not None else None
    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        width=width,
        height=height,
        generator=gen,
    ).images[0]

    ts = time.strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"t2i_{ts}.png"
    image.save(path)
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prompt", required=True, help="Text prompt")
    ap.add_argument("-n", "--negative-prompt", default=None)
    ap.add_argument("-o", "--out", default=str(IMAGES_DIR))
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--steps", type=int, default=4, help="Fewer steps for sd-turbo is fine (fast)")
    ap.add_argument("--guidance", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--model", default="stabilityai/sd-turbo")
    ap.add_argument("--no-enhance", action="store_true", help="Disable cinematic/8k boost")
    args = ap.parse_args()

    path = generate_image(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        width=args.width,
        height=args.height,
        steps=args.steps,
        guidance=args.guidance,
        seed=args.seed,
        model_id=args.model,
        enhance=(not args.no_enhance),
        out_dir=Path(args.out),
    )
    print(str(path))

if __name__ == "__main__":
    main()
