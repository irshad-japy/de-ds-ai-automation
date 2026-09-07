from __future__ import annotations

import argparse
from pathlib import Path

from common.adls import upload_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload an orders CSV into ADLS raw/orders")
    parser.add_argument("--file", default="data/synthetic/orders_001.csv")
    parser.add_argument("--remote-path", default="raw/orders/orders_001.csv")
    args = parser.parse_args()
    local = Path(args.file)
    if not local.exists():
        raise FileNotFoundError(local)
    upload_file(local, args.remote_path)
    print(f"[SUCCESS] Uploaded {local} -> {args.remote_path}")


if __name__ == "__main__":
    main()
