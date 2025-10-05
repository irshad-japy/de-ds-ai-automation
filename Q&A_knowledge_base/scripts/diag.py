"""
poetry run python scripts/diag.py
"""

#!/usr/bin/env python
import httpx, os, sys, json
from lr.config import settings

def check_qdrant():
    url = f"http://{settings.qdrant_host}:{settings.qdrant_port}/collections"
    try:
        r = httpx.get(url, timeout=5.0)
        return {"ok": r.status_code == 200, "status": r.status_code, "body": r.text[:300]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_ollama():
    base = settings.ollama_base.rstrip("/")
    try:
        # models
        r = httpx.get(f"{base}/api/tags", timeout=5.0)
        models = [m.get("name") for m in (r.json().get("models", []) if r.headers.get("content-type","").startswith("application/json") else [])]
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "models": models}

if __name__ == "__main__":
    print(json.dumps({
        "provider": settings.provider,
        "qdrant": check_qdrant(),
        "ollama": check_ollama(),
    }, indent=2))
