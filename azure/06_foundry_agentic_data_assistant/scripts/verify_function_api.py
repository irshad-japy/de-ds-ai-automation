from __future__ import annotations

import os
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def get(route, params=None, use_key=True):
    base = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071/api").rstrip("/")
    headers = {}
    if use_key and os.getenv("FUNCTION_KEY"):
        headers["x-functions-key"] = os.environ["FUNCTION_KEY"]
    r = requests.get(f"{base}/{route}", params=params, headers=headers, timeout=20)
    print(route, r.status_code, r.text)
    r.raise_for_status()
    return r.json()


def main():
    get("health", use_key=False)
    get("revenue-by-region", {"start_date": "2026-09-01", "end_date": "2026-09-02"})
    get("delayed-shipments", {"date": "2026-09-02"})
    get("order-summary", {"order_id": 1001})
    get("metric-source", {"metric_name": "revenue"})
    print("[SUCCESS] Function API endpoints verified.")


if __name__ == "__main__":
    main()
