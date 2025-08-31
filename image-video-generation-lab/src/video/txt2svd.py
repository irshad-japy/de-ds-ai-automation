"""
python src/video/txt2svd.py --prompt "cinematic slow-motion shot of waves crashing on a rocky beach at sunset, 35mm film look, natural lighting" --seconds 1.8 --fps 25 --width 768 --height 768 --out out_svd.mp4
"""

import argparse, os, numpy as np
import torch, imageio
from diffusers import AutoPipelineForText2Image, StableVideoDiffusionPipeline

def save_mp4(frames01, path, fps=25):
    arr = (np.clip(frames01, 0, 1) * 255).astype("uint8")
    imageio.mimwrite(path, arr, fps=fps, quality=7)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="Text prompt for the still image")
    ap.add_argument("--seconds", type=float, default=1.6, help="seconds of motion per clip")
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--t2i_model", default="stabilityai/sdxl-turbo")
    ap.add_argument("--svd_model", default="stabilityai/stable-video-diffusion-img2vid-xt")
    ap.add_argument("--t2i_steps", type=int, default=4)
    ap.add_argument("--t2i_guidance", type=float, default=0.0)
    ap.add_argument("--motion", type=int, default=127, help="SVD motion_bucket_id (0-255)")
    ap.add_argument("--noise_aug", type=float, default=0.02)
    ap.add_argument("--out", default="out_svd.mp4")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--offload", action="store_true", help="Enable CPU offload to reduce VRAM")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    generator = torch.Generator(device=device).manual_seed(args.seed)

    # 1) Text -> Image (use AutoPipelineForText2Image for SDXL-family)
    print("Loading T2I:", args.t2i_model)
    t2i = AutoPipelineForText2Image.from_pretrained(args.t2i_model, torch_dtype=dtype).to(device)
    if args.offload and device == "cuda":
        t2i.enable_model_cpu_offload()

    print("Generating still image...")
    img = t2i(
        prompt=args.prompt,
        guidance_scale=args.t2i_guidance,    # 0.0 is fine for SDXL-Turbo
        num_inference_steps=args.t2i_steps,  # turbo often works in 1–4 steps
        height=args.height,
        width=args.width,
        generator=generator
    ).images[0]

    # 2) Image -> Video (SVD)
    print("Loading SVD:", args.svd_model)
    svd = StableVideoDiffusionPipeline.from_pretrained(args.svd_model, torch_dtype=dtype).to(device)
    if args.offload and device == "cuda":
        svd.enable_model_cpu_offload()

    num_frames = int(args.fps * args.seconds)
    print(f"Animating with SVD: {num_frames} frames @ {args.fps} fps (motion={args.motion})")
    out = svd(
        image=img,
        num_frames=num_frames,
        fps=args.fps,
        motion_bucket_id=args.motion,
        noise_aug_strength=args.noise_aug,
        decode_chunk_size=8,
        generator=generator
    )
    frames = out.frames[0]  # (F, H, W, 3) in [0,1]

    # 3) Save MP4
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    save_mp4(frames, args.out, fps=args.fps)
    print("Saved:", args.out)

if __name__ == "__main__":
    main()
