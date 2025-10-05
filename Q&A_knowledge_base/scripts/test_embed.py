"""
poetry run python scripts/test_embed.py
"""

#!/usr/bin/env python
import os, httpx, json
from lr.config import settings

def main():
    text = "hello world"
    base = settings.ollama_base.rstrip("/")
    model = settings.ollama_embed_model
    print(f"Using base={base}, model={model}")

    with httpx.Client(timeout=60.0) as c:
        r = c.post(f"{base}/api/embeddings", json={"model": model, "prompt": text})
        print("status:", r.status_code)
        print("raw:", r.text[:300])  # show first 300 chars

        js = r.json()
        # Common shapes:
        #  - {"embedding":[...]}
        #  - {"data":[{"embedding":[...]}]}
        #  - {"embeddings":[[...]]}  (rare)
        vec = None
        if isinstance(js, dict):
            if "embedding" in js:
                vec = js["embedding"]
            elif "data" in js and isinstance(js["data"], list) and js["data"]:
                vec = js["data"][0].get("embedding")
            elif "embeddings" in js and isinstance(js["embeddings"], list) and js["embeddings"]:
                vec = js["embeddings"][0]
        if vec is None:
            raise SystemExit(f"Could not find embedding in response: {js}")
        print("dim:", len(vec))
        if len(vec) == 0:
            raise SystemExit("Embedding has length 0 (bad). Check model and server.")

if __name__ == "__main__":
    main()
