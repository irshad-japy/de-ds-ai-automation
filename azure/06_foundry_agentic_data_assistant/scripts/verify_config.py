from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

REQUIRED = ["FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_MODEL_DEPLOYMENT_NAME", "FOUNDRY_AGENT_NAME"]
OPTIONAL = ["SEARCH_CONNECTION_NAME", "SEARCH_INDEX_NAME", "FUNCTION_BASE_URL", "APPLICATIONINSIGHTS_CONNECTION_STRING"]


def masked(value: str) -> str:
    if not value:
        return "<not set>"
    return value if len(value) < 10 else value[:5] + "..." + value[-3:]


def main():
    print("POC-06 configuration check")
    print("Python:", sys.version.split()[0])
    print("Azure CLI:", shutil.which("az") or "NOT FOUND")
    print("Functions Core Tools:", shutil.which("func") or "NOT FOUND (only needed for local/deploy Function App)")
    print()

    missing = []
    for name in REQUIRED:
        value = os.getenv(name, "")
        print(f"{name}: {masked(value)}")
        if not value:
            missing.append(name)
    for name in OPTIONAL:
        print(f"{name}: {masked(os.getenv(name, ''))}")

    backend = os.getenv("TOOL_BACKEND", "mock")
    print("TOOL_BACKEND:", backend)
    print(".env exists:", (ROOT / ".env").exists())

    if missing:
        print("\n[FAIL] Missing required variables:", ", ".join(missing))
        raise SystemExit(1)
    print("\n[SUCCESS] Base configuration looks valid.")


if __name__ == "__main__":
    main()
