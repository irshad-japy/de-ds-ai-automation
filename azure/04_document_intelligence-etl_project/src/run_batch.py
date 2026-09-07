from __future__ import annotations

import argparse
import json

from .config import get_settings
from .pipeline import InvoicePipeline
from .storage_client import StorageRepository


def main() -> int:
    parser = argparse.ArgumentParser(description="Process invoice PDFs/images from Azure Blob/ADLS Gen2.")
    parser.add_argument("--prefix", default="incoming/", help="Blob prefix to process")
    parser.add_argument("--blob", help="Process only one exact blob name")
    args = parser.parse_args()

    settings = get_settings()
    storage = StorageRepository(settings)
    pipeline = InvoicePipeline(settings, storage)

    blob_names = [args.blob] if args.blob else list(storage.list_blobs(args.prefix))
    if not blob_names:
        print(f"No blobs found under prefix: {args.prefix}")
        return 1

    summary = {"processed": 0, "failed": 0, "skipped": 0}
    for blob_name in blob_names:
        try:
            result = pipeline.process_blob(blob_name)
            print(json.dumps(result, indent=2, default=str))
            status = result.get("status", "")
            if status == "processed":
                summary["processed"] += 1
            elif status.startswith("skipped"):
                summary["skipped"] += 1
            else:
                summary["failed"] += 1
        except Exception as exc:
            summary["failed"] += 1
            print(json.dumps({"blob": blob_name, "error": str(exc)}, indent=2))

    print("\nSUMMARY")
    print(json.dumps(summary, indent=2))
    return 0 if summary["processed"] or summary["skipped"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
