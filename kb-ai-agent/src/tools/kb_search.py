"""
python -m src.tools.kb_search
"""

# src/tools/kb_search.py
import os
import time
from typing import List, Tuple, Dict, Any, Optional

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(filename=".env"), override=True)

import chromadb
from chromadb.config import Settings

# Your project util that returns an embeddings object with either
# .embed_query(text) or .embed_documents(list[str]) available.
from ..util.llm import get_embeddings

# --- Env / Config ---
CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_TENANT: str = os.getenv("CHROMA_TENANT", "default_tenant")
CHROMA_DATABASE: str = os.getenv("CHROMA_DATABASE", "default_database")
COLLECTION: str = os.getenv("CHROMA_COLLECTION", "knowledge_base")

# --- Client helpers ---
def _get_client() -> chromadb.HttpClient:
    # Settings() is fine; HttpClient handles REST.
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        settings=Settings(),
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
    )

CLIENT = _get_client()

def _wait_until_ready(client: chromadb.HttpClient, attempts: int = 20, sleep_s: float = 0.2) -> None:
    for _ in range(attempts):
        try:
            client.list_collections()
            return
        except Exception:
            time.sleep(sleep_s)

def _get_collection(name: str):
    # Do NOT pass embedding_function here; we supply query_embeddings manually.
    return CLIENT.get_or_create_collection(name=name)

# --- Public API ---
def search_kb(query: str, k: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Vector-search the KB and return a list of (document, metadata) pairs.
    This aligns with your `ask` CLI which unpacks (doc, meta).
    """
    _wait_until_ready(CLIENT)  # mirrors your POC's readiness loop

    kb = _get_collection(COLLECTION)

    # Build a single query vector using your embedding helper.
    emb = get_embeddings()
    if hasattr(emb, "embed_query"):
        qvec = emb.embed_query(query)  # -> List[float]
    else:
        qvec = emb.embed_documents([query])[0]  # -> List[float]

    # Query with vectors; ids are always present; include docs+metas for display.
    res = kb.query(
        query_embeddings=[qvec],
        n_results=max(1, int(k)),
        include=["documents", "metadatas", "distances"],  # distances useful for debugging
    )

    # Defensive unpacking (Chroma returns lists-of-lists)
    docs: List[str] = (res.get("documents") or [[]])[0] or []
    metas: List[Dict[str, Any]] = (res.get("metadatas") or [[]])[0] or []
    # If you ever want to use distances for sorting/debugging:
    # dists: List[float] = (res.get("distances") or [[]])[0] or []

    # Zip to match your CLI’s expectation (doc, meta)
    return list(zip(docs, metas))

# --- Smoke test (optional) ---
if __name__ == "__main__":
    _wait_until_ready(CLIENT)
    try:
        print("Heartbeat:", CLIENT.heartbeat())
    except Exception as e:
        print("Heartbeat failed:", e)

    print(f"Querying collection: {COLLECTION!r}")
    hits = search_kb("quick smoke test", k=3)
    print("Hits:", len(hits))
    for i, (doc, meta) in enumerate(hits, 1):
        src = meta.get("source") if isinstance(meta, dict) else None
        preview = (doc or "")[:300]
        print(f"[{i}] src={src}\n{preview}\n")
