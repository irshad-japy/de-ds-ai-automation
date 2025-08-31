# src/video/svd_img2vid.py
from pathlib import Path
from typing import List, Optional
import torch
import numpy as np
import cv2

from PIL import Image
# src/video/svd_img2vid.py
from diffusers import StableVideoDiffusionPipeline

def load_svd(model_id: str = "stabilityai/stable-video-diffusion-img2vid-xt"):
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        variant="fp16" if torch.cuda.is_available() else None,
    )

    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    else:
        # pure CPU
        pipe = pipe.to("cpu")
        # optional memory savers (guarded by hasattr to avoid AttributeErrors)
        try:
            pipe.enable_attention_slicing()
        except AttributeError:
            pass

        # On some diffusers versions, slicing/tiling live on the VAE module
        if hasattr(pipe, "vae") and hasattr(pipe.vae, "enable_slicing"):
            pipe.vae.enable_slicing()
        if hasattr(pipe, "vae") and hasattr(pipe.vae, "enable_tiling"):
            # tiling helps at higher resolutions; harmless at low res
            pipe.vae.enable_tiling()

    return pipe


def img_to_video(
    pipe: StableVideoDiffusionPipeline,
    image_path: Path,
    motion_bucket_id: int = 127,     # 0..255 (higher = more motion)
    noise_aug_strength: float = 0.05,
    num_frames: int = 25,            # ~1 sec at 24–25 fps
    fps: int = 25,
    decode_chunk_size: int = 8,
    seed: Optional[int] = None,
) -> List[np.ndarray]:
    image = Image.open(image_path).convert("RGB")
    image = image.resize((768, 448))  # SVD likes 16-multiple sizes; common preset
    generator = torch.Generator(device=pipe.device) if seed is not None else None
    if seed is not None:
        generator.manual_seed(seed)

    result = pipe(
        image=image,
        num_frames=num_frames,
        decode_chunk_size=decode_chunk_size,
        motion_bucket_id=motion_bucket_id,
        noise_aug_strength=noise_aug_strength,
        generator=generator,
    )
    # result.frames: [T, H, W, C] uint8
    frames = [np.array(frame) for frame in result.frames]
    return frames

def write_video(frames: List[np.ndarray], out_path: Path, fps: int = 25) -> Path:
    h, w, _ = frames[0].shape
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # libx264 requires ffmpeg binding; mp4v okay
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    for f in frames:
        writer.write(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
    writer.release()
    return out_path
