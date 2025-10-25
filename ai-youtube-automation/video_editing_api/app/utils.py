from __future__ import annotations
import shutil, subprocess, json, re
from pathlib import Path
from typing import Optional

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
INPUT_DIR = Path(__file__).resolve().parent.parent / "input"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
INPUT_DIR.mkdir(parents=True, exist_ok=True)

def which(name: str) -> Optional[str]:
    return shutil.which(name)

def require_ffmpeg() -> str:
    ff = which("ffmpeg")
    if not ff:
        raise RuntimeError("ffmpeg not found on PATH")
    return ff

def get_video_metadata(path: Path) -> dict:
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Video not found: {path}")
    meta = {
        "filename": path.name,
        "abs_path": str(path.resolve()),
        "size_mb": round(path.stat().st_size/(1024*1024), 2),
        "duration_s": None
    }
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        try:
            out = subprocess.run(
                [ffprobe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "json", str(path)],
                capture_output=True, text=True
            )
            j = json.loads(out.stdout or "{}")
            dur = float(j.get("format", {}).get("duration", 0.0))
            if dur > 0:
                meta["duration_s"] = round(dur, 2)
        except Exception:
            pass
    return meta

def save_json(obj: dict, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return dest

def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def clean_topic(s: str) -> str:
    return re.sub(r"[_\-]+", " ", Path(s).stem).strip().title()
