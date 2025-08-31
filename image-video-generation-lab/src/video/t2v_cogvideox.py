"""
python src/video/t2v_cogvideox.py --repo zai-org/CogVideoX-2b --width 768 --height 448 --frames 61 --steps 24 --prompt "a serene waterfall in a mossy forest, cinematic, realistic"
"""

import argparse, os, numpy as np, torch, imageio
from diffusers import DiffusionPipeline

def save_mp4(frames01, path, fps=25):
    arr = (np.clip(frames01, 0, 1) * 255).astype("uint8")
    imageio.mimwrite(path, arr, fps=fps, quality=7)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--repo", default="zai-org/CogVideoX1.5-5B", help="Use 'zai-org/CogVideoX-2b' for 12GB GPUs")
    ap.add_argument("--frames", type=int, default=81)      # ~3.2s @ 25 fps
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--guidance", type=float, default=3.5)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=576)
    ap.add_argument("--out", default="out_t2v.mp4")
    ap.add_argument("--offload", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    generator = torch.Generator(device=device).manual_seed(args.seed)

    print("Loading:", args.repo)
    pipe = DiffusionPipeline.from_pretrained(args.repo, torch_dtype=dtype)
    pipe = pipe.to(device)
    if args.offload and device == "cuda":
        pipe.enable_model_cpu_offload()
        # pipe.enable_vae_slicing()

    print("Generating...")
    out = pipe(
        prompt=args.prompt,
        num_frames=args.frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        fps=args.fps,
        height=args.height,
        width=args.width,
        generator=generator
    )
    frames = out.videos[0]  # shape: (F, H, W, 3) in [0,1]

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    save_mp4(frames, args.out, fps=args.fps)
    print("Saved:", args.out)

if __name__ == "__main__":
    main()
