import os
from pathlib import Path
from ..config import settings


ART = Path(settings.ARTIFACTS_DIR)
ART.mkdir(parents=True, exist_ok=True)
BASE_ARTIFACT_DIR = Path("artifacts")

def ensure_dir(item_id: str, filename: str) -> Path:
    """
    Ensure that artifacts/<item_id>/ exists and return the full file path.
    Always returns a pathlib.Path object.
    """
    # ✅ Use only one root 'artifacts' directory
    target_dir = BASE_ARTIFACT_DIR / str(item_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / filename