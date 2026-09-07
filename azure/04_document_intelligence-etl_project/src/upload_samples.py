from __future__ import annotations

import argparse
from pathlib import Path

from .config import get_settings
from .storage_client import StorageRepository

def main() -> int:
    parser = argparse.ArgumentParser(description="Upload synthetic sample invoices to incoming/.")
    parser.add_argument("--dir", default="samples/input", help="Local directory containing PDFs/images")
    args = parser.parse_args()

    root = Path(args.dir)
    files = sorted([p for p in root.iterdir() if p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"}])
    if not files:
        print(f"No sample documents found in {root}")
        return 1

    settings = get_settings()
    storage = StorageRepository(settings)
    storage.ensure_container()

    for path in files:
        blob_name = f"incoming/{path.name}"
        storage.upload_bytes(blob_name, path.read_bytes(), overwrite=True)
        print(f"Uploaded: {path} -> {settings.storage_container}/{blob_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
