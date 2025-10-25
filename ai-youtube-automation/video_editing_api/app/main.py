from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional

from .utils import OUTPUT_DIR, INPUT_DIR, which, get_video_metadata, save_json
from .audio import denoise_and_normalize, ffmpeg_replace_audio, tts_synthesize_to_wav, estimate_rate_for_duration
from .trim_detect import auto_trim_blank
from .ocr_privacy import auto_blur_sensitive
from .editing import replace_audio_track
from .scriptgen import build_autoscript
import subprocess
from typing import List

app = FastAPI(title="Advanced Video Editing API", version="1.0.0")

class DenoiseRequest(BaseModel):
    video_path: str
    out_name: Optional[str] = None
    use_rnnoise: bool = False

class TrimRequest(BaseModel):
    video_path: str
    out_name: Optional[str] = None

class BlurRequest(BaseModel):
    video_path: str
    out_name: Optional[str] = None
    sample_every: float = Field(0.8, ge=0.2, le=5.0)
    radius: float = Field(0.6, ge=0.2, le=3.0)
    min_line_len: int = Field(10, ge=3, le=50)

class CleanupRequest(BaseModel):
    video_path: str
    out_name: Optional[str] = None
    use_rnnoise: bool = False
    sample_every: float = 1.0
    min_line_len: int = 10

class AutoScriptRequest(BaseModel):
    video_path: str
    sample_every: float = Field(1.2, ge=0.2, le=5.0)
    scene_sensitivity: float = Field(0.25, ge=0.05, le=0.9)
    target_seconds: int = Field(75, ge=20, le=900)
    min_line_len: int = Field(10, ge=3, le=50)
    max_lines: int = Field(16, ge=4, le=40)

class NarrateRequest(BaseModel):
    voiceover_json_path: str
    video_path: str
    voice_id: Optional[str] = None
    rate: Optional[int] = None
    volume: float = 1.0
    target_seconds: Optional[int] = None
    loudnorm: bool = True

class ReplaceAudioRequest(BaseModel):
    video_path: str
    audio_path: str
    out_name: Optional[str] = None
    loudnorm: bool = True

class ProduceFullRequest(BaseModel):
    video_path: str
    target_seconds: int = 75
    loudnorm: bool = True

@app.get("/health")
def health():
    return {
        "ffmpeg": bool(which("ffmpeg")),
        "ffprobe": bool(which("ffprobe")),
        "tesseract": bool(which("tesseract")),
        "input_dir": str(INPUT_DIR),
        "output_dir": str(OUTPUT_DIR)
    }

@app.post("/denoise_normalize")
def api_denoise(req: DenoiseRequest):
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")
    out = OUTPUT_DIR / (req.out_name or f"{src.stem}_clean.mp4")
    try:
        denoise_and_normalize(src, out, use_rnnoise=req.use_rnnoise)
    except Exception as e:
        raise HTTPException(500, f"ffmpeg failed: {e}")
    return {"saved_video": str(out.resolve())}

@app.post("/auto_trim_blank")
def api_trim(req: TrimRequest):
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")
    out = OUTPUT_DIR / (req.out_name or f"{src.stem}_trim.mp4")
    try:
        keeps = auto_trim_blank(src, out)
    except Exception as e:
        raise HTTPException(500, f"trim failed: {e}")
    return {"saved_video": str(out.resolve()), "kept_segments": keeps}

@app.post("/auto_blur_sensitive")
def api_blur(req: BlurRequest):
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")
    out = OUTPUT_DIR / (req.out_name or f"{src.stem}_blur.mp4")
    try:
        auto_blur_sensitive(str(src), str(out), sample_every=req.sample_every, radius=req.radius, min_line_len=req.min_line_len)
    except Exception as e:
        raise HTTPException(500, f"blur failed: {e}")
    return {"saved_video": str(out.resolve())}

@app.post("/cleanup")
def api_cleanup(req: CleanupRequest):
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")
    tmp1 = OUTPUT_DIR / f"{src.stem}_trim.mp4"
    tmp2 = OUTPUT_DIR / f"{src.stem}_clean.mp4"
    out  = OUTPUT_DIR / (req.out_name or f"{src.stem}_cleaned.mp4")
    try:
        auto_trim_blank(src, tmp1)
        from .audio import denoise_and_normalize as _den
        _den(tmp1, tmp2, use_rnnoise=req.use_rnnoise)
        from .ocr_privacy import auto_blur_sensitive as _blur
        _blur(str(tmp2), str(out), sample_every=req.sample_every, min_line_len=req.min_line_len)
    except Exception as e:
        raise HTTPException(500, f"cleanup failed: {e}")
    return {"saved_video": str(out.resolve())}

@app.post("/autoscript")
def api_autoscript(req: AutoScriptRequest):
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")
    try:
        dest, payload = build_autoscript(src, req.sample_every, req.scene_sensitivity, req.target_seconds, req.min_line_len, req.max_lines)
    except Exception as e:
        raise HTTPException(500, f"autoscript failed: {e}")
    return {"saved_json": dest, **payload}

@app.post("/produce_narrated")
def api_narrated(req: NarrateRequest):
    jpath = Path(req.voiceover_json_path)
    if not jpath.exists():
        raise HTTPException(404, f"Not found: {jpath}")
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")
    try:
        import json
        payload = json.loads(jpath.read_text(encoding="utf-8"))
        script = payload["voiceover_script"]
    except Exception:
        raise HTTPException(400, "Invalid voiceover json")
    words = len(script.split())
    meta = get_video_metadata(src)
    tsec = req.target_seconds or int(meta.get("duration_s") or 0) or 60
    rate = req.rate or estimate_rate_for_duration(words, tsec)
    wav = OUTPUT_DIR / f"{src.stem}_narration.wav"
    try:
        tts_synthesize_to_wav(script, wav, req.voice_id, rate, req.volume)
    except Exception as e:
        raise HTTPException(500, f"TTS failed: {e}")
    outv = OUTPUT_DIR / f"{src.stem}_narrated.mp4"
    try:
        ffmpeg_replace_audio(src, wav, outv, loudnorm=req.loudnorm)
    except Exception as e:
        raise HTTPException(500, f"merge failed: {e}")
    return {"narration_wav": str(wav.resolve()), "saved_video": str(outv.resolve())}

@app.post("/replace_audio")
def api_replace(req: ReplaceAudioRequest):
    src = Path(req.video_path); aud = Path(req.audio_path)
    if not src.exists() or not aud.exists():
        raise HTTPException(404, "video or audio not found")
    out = OUTPUT_DIR / (req.out_name or f"{src.stem}_replaced.mp4")
    try:
        if req.loudnorm:
            ffmpeg_replace_audio(src, aud, out, loudnorm=True)
        else:
            from .editing import replace_audio_track
            replace_audio_track(src, aud, out)
    except Exception as e:
        raise HTTPException(500, f"replace failed: {e}")
    return {"saved_video": str(out.resolve())}

@app.post("/produce_full")
def api_full(req: ProduceFullRequest):
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")
    try:
        jpath, payload = build_autoscript(src, 1.0, 0.20, req.target_seconds, 10, 18)
    except Exception as e:
        raise HTTPException(500, f"autoscript failed: {e}")
    import json
    script = payload["voiceover_script"]
    words = len(script.split())
    rate = estimate_rate_for_duration(words, req.target_seconds)
    wav = OUTPUT_DIR / f"{src.stem}_narration.wav"
    try:
        tts_synthesize_to_wav(script, wav, None, rate, 1.0)
    except Exception as e:
        raise HTTPException(500, f"TTS failed: {e}")
    outv = OUTPUT_DIR / f"{src.stem}_full.mp4"
    try:
        ffmpeg_replace_audio(src, wav, outv, loudnorm=req.loudnorm)
    except Exception as e:
        raise HTTPException(500, f"merge failed: {e}")
    return {"voiceover_json": jpath, "narration_wav": str(wav.resolve()), "saved_video": str(outv.resolve())}


# ADD:
def _ff_norm_font_path(p: str) -> str:
    """
    Make a Windows font path safe for ffmpeg drawtext:
    - use forward slashes
    - escape the drive-letter colon as '\:'
    Example: 'C:\\Windows\\Fonts\\arialbd.ttf' -> 'C\\:/Windows/Fonts/arialbd.ttf'
    """
    s = p.replace("\\", "/")      # C:\Windows\Fonts\... -> C:/Windows/Fonts/...
    s = s.replace(":", r"\:")     # C:/... -> C\:/...
    return s



# ADD:
class ThumbnailRequest(BaseModel):
    video_path: str
    at_seconds: float = 7.0

    # output size
    width: int = 1280
    height: int = 720

    # background styling
    blur_sigma: float = 16.0
    darken: float = -0.06         # ffmpeg eq: negative is darker
    contrast: float = 1.10

    # right-side info card
    overlay_title: Optional[str] = "Automate Tasks"
    overlay_sub: Optional[str] = "in 1 Minute"
    overlay_small: Optional[str] = "Step by Step"

    bar_color: str = "white@0.85"
    bar_x: Optional[int] = None   # auto to right if None
    bar_y: int = 130
    bar_w: int = 480
    bar_h: int = 460

    # font (Windows default; change for mac/linux)
    font_path: str = r"C:\Windows\Fonts\arialbd.ttf"
    title_size: int = 82
    sub_size: int = 82
    small_size: int = 60
    font_color: str = "black"
    borderw: int = 0               # outline width (e.g., 4–6 if no card)
    bordercolor: str = "black@0.9"

    # optional logo
    logo_path: Optional[str] = None
    logo_width: int = 220
    logo_x: int = 40
    logo_y: int = 40

    # output filename
    out_name: Optional[str] = None  # default: <video>_thumb.jpg

class ThumbnailResponse(BaseModel):
    saved_path: str
    used_timecode: float
    meta: dict

class ThumbnailBatchRequest(BaseModel):
    video_path: str
    timestamps: Optional[List[float]] = None  # OR:
    evenly_n: Optional[int] = None
    start_at: float = 5.0
    end_at: Optional[float] = None

    # styling (applied to all)
    width: int = 1280
    height: int = 720
    blur_sigma: float = 16.0
    darken: float = -0.06
    contrast: float = 1.10
    overlay_title: Optional[str] = "Automate Tasks"
    overlay_sub: Optional[str] = "in 1 Minute"
    overlay_small: Optional[str] = "Step by Step"
    bar_color: str = "white@0.85"
    font_path: str = r"C:\Windows\Fonts\arialbd.ttf"
    title_size: int = 82
    sub_size: int = 82
    small_size: int = 60
    font_color: str = "black"
    borderw: int = 0
    bordercolor: str = "black@0.9"
    logo_path: Optional[str] = None
    logo_width: int = 220
    logo_x: int = 40
    logo_y: int = 40

class ThumbnailBatchResponse(BaseModel):
    generated: List[ThumbnailResponse]


# ADD:
def _ff_esc_text(s: str) -> str:
    """Escape a string for ffmpeg drawtext (single-quoted)."""
    s = s.replace("\\", "\\\\")
    s = s.replace(":", r"\:")
    s = s.replace("'", r"\'")
    s = s.replace("\n", r"\n")
    return s

def _auto_bar_x(width: int, bar_w: int, margin: int = 60) -> int:
    """Right-align the info card with a margin."""
    return max(0, width - bar_w - margin)


# ADD:
@app.post("/thumbnail", response_model=ThumbnailResponse)
def api_thumbnail(req: ThumbnailRequest):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(501, "ffmpeg not found on PATH or FFMPEG_BIN")
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")

    try:
        meta = get_video_metadata(src)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))

    out_name = req.out_name or f"{src.stem}_thumb.jpg"
    stage = OUTPUT_DIR / f"__{src.stem}_thumb_stage.jpg"
    final = OUTPUT_DIR / out_name

    bx = req.bar_x if req.bar_x is not None else _auto_bar_x(req.width, req.bar_w)
    font_path_use = _ff_norm_font_path(req.font_path)
    vf_parts = [
        f"scale={req.width}:{req.height}",
        f"gblur=sigma={req.blur_sigma}",
        f"eq=brightness={req.darken}:contrast={req.contrast}",
        f"drawbox=x={bx}:y={req.bar_y}:w={req.bar_w}:h={req.bar_h}:color={req.bar_color}:t=fill"
    ]

    if req.overlay_title:
        t = _ff_esc_text(req.overlay_title)
        vf_parts.append(
            f"drawtext=fontfile='{font_path_use}':text='{t}':fontcolor={req.font_color}:fontsize={req.title_size}"
            f":x={bx+30}:y={req.bar_y+40}:borderw={req.borderw}:bordercolor={req.bordercolor}"
        )
    if req.overlay_sub:
        t = _ff_esc_text(req.overlay_sub)
        vf_parts.append(
            f"drawtext=fontfile='{font_path_use}':text='{t}':fontcolor={req.font_color}:fontsize={req.sub_size}"
            f":x={bx+30}:y={req.bar_y+150}:borderw={req.borderw}:bordercolor={req.bordercolor}"
        )
    if req.overlay_small:
        t = _ff_esc_text(req.overlay_small)
        vf_parts.append(
            f"drawtext=fontfile='{font_path_use}':text='{t}':fontcolor={req.font_color}:fontsize={req.small_size}"
            f":x={bx+30}:y={req.bar_y+270}:borderw={req.borderw}:bordercolor={req.bordercolor}"
        )

    vf = ",".join(vf_parts)

    # 1) render processed frame at timestamp
    cmd1 = [
        ff, "-hide_banner", "-y",
        "-ss", f"{req.at_seconds:.3f}",
        "-i", str(src),
        "-vframes", "1",
        "-vf", vf,
        str(stage)
    ]
    p1 = subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p1.returncode != 0:
        tail = "\n".join(p1.stderr.strip().splitlines()[-20:])
        raise HTTPException(status_code=500, detail=f"ffmpeg (frame render) failed:\n{tail}")

    # 2) optional logo overlay
    if req.logo_path and Path(req.logo_path).exists():
        cmd2 = [
            ff, "-hide_banner", "-y",
            "-i", str(stage),
            "-i", str(req.logo_path),
            "-filter_complex", f"[1:v]scale={req.logo_width}:-1[lg];[0:v][lg]overlay={req.logo_x}:{req.logo_y}",
            str(final)
        ]
        p2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p2.returncode != 0:
            tail = "\n".join(p2.stderr.strip().splitlines()[-20:])
            raise HTTPException(status_code=500, detail=f"ffmpeg (logo overlay) failed:\n{tail}")
    else:
        stage.replace(final)

    return ThumbnailResponse(
        saved_path=str(final.resolve()),
        used_timecode=req.at_seconds,
        meta={"width": req.width, "height": req.height, "bar_x": bx}
    )

# ADD:
@app.post("/thumbnails/batch", response_model=ThumbnailBatchResponse)
def api_thumbnails_batch(req: ThumbnailBatchRequest):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(501, "ffmpeg not found on PATH or FFMPEG_BIN")
    src = Path(req.video_path)
    if not src.exists():
        raise HTTPException(404, f"Not found: {src}")

    meta = get_video_metadata(src)
    duration = float(meta.get("duration_s") or 0.0)
    if req.end_at is None:
        req.end_at = max(0.0, duration - 1.0)

    # Build timestamps
    if req.timestamps:
        times = [max(0.0, min(float(t), duration)) for t in req.timestamps]
    else:
        n = max(1, int(req.evenly_n or 5))
        if req.end_at <= req.start_at:
            raise HTTPException(400, "end_at must be greater than start_at for evenly spaced thumbnails.")
        step = (req.end_at - req.start_at) / n
        times = [round(req.start_at + i*step, 2) for i in range(n)]

    results: List[ThumbnailResponse] = []
    for i, t in enumerate(times, start=1):
        one = ThumbnailRequest(
            video_path=req.video_path,
            at_seconds=t,
            width=req.width, height=req.height,
            blur_sigma=req.blur_sigma, darken=req.darken, contrast=req.contrast,
            overlay_title=req.overlay_title, overlay_sub=req.overlay_sub, overlay_small=req.overlay_small,
            bar_color=req.bar_color,
            font_path=req.font_path, title_size=req.title_size, sub_size=req.sub_size, small_size=req.small_size,
            font_color=req.font_color, borderw=req.borderw, bordercolor=req.bordercolor,
            logo_path=req.logo_path, logo_width=req.logo_width, logo_x=req.logo_x, logo_y=req.logo_y,
            out_name=f"{src.stem}_thumb_{i:02d}.jpg"
        )
        res = api_thumbnail(one)  # reuse single endpoint logic
        results.append(res)

    return ThumbnailBatchResponse(generated=results)
