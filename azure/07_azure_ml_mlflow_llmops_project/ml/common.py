from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
TRAIN_DIR = DATA_DIR / "train"
SCORING_DIR = DATA_DIR / "scoring"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MLRUNS_DIR = PROJECT_ROOT / "mlruns"

FEATURES = [
    "origin_region",
    "destination_region",
    "carrier",
    "distance_km",
    "order_hour",
    "weekday",
    "priority",
    "historical_delay_rate",
]
TARGET = "is_delayed"
CATEGORICAL_FEATURES = [
    "origin_region",
    "destination_region",
    "carrier",
    "priority",
]
NUMERIC_FEATURES = [
    "distance_km",
    "order_hour",
    "weekday",
    "historical_delay_rate",
]


def ensure_dirs() -> None:
    for p in [TRAIN_DIR, SCORING_DIR, OUTPUT_DIR, MLRUNS_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_code_version() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return os.getenv("CODE_VERSION", "not-a-git-clone")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def require_columns(columns: Iterable[str]) -> None:
    missing = [c for c in FEATURES if c not in columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")
