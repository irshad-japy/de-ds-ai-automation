"""
python -m src.tools.kb_ingest

# (1) Quick env check (optional)
poetry run python -c "from dotenv import load_dotenv, find_dotenv; load_dotenv(find_dotenv('.env'), override=True); import os; print('MODE', os.getenv('CHROMA_MODE')); print('HOST', os.getenv('CHROMA_HOST')); print('PORT', os.getenv('CHROMA_PORT')); print('TENANT', os.getenv('CHROMA_TENANT')); print('DB', os.getenv('CHROMA_DATABASE')); print('COLL', os.getenv('CHROMA_COLLECTION'))"

# (2) Heartbeat (optional, if CHROMA_MODE=http and server is running)
poetry run python -m src.tools.kb_ingest --heartbeat

# (3) Ingest PDFs and JSONL in one go
poetry run python -m src.tools.kb_ingest --pdf-dir data/raw --url-file urls.jsonl

"""


# src/tools/kb_ingest.py
import os
import json
import argparse
from typing import List, Dict, Optional, Tuple

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(filename=".env", usecwd=True), override=True)

# Project utilities
from ..util.chunking import simple_chunk
from ..util.llm import get_embeddings


# -------------------- ENV --------------------
CHROMA_MODE = os.getenv("CHROMA_MODE", "http").strip().lower()   # "http" | "local"
INDEX_DIR = os.getenv("INDEX_DIR", "./data/index")
COLLECTION = os.getenv("CHROMA_COLLECTION", "knowledge_base")    # >=3 chars, alnum start/end
os.environ.setdefault("CHROMA_TELEMETRY_ENABLED", os.getenv("CHROMA_TELEMETRY_ENABLED", "false"))

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "default_tenant")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "default_database")


# -------------------- CHROMA CLIENT --------------------
def _get_chroma_client():
    import chromadb
    from chromadb.config import Settings
    if CHROMA_MODE == "http":
        return chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            settings=Settings(),
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
        )
    # local embedded (duckdb+parquet)
    return chromadb.Client(
        Settings(chroma_db_impl="duckdb+parquet", persist_directory=INDEX_DIR)
    )


def _ensure_collection(client, name: Optional[str] = None):
    name = name or COLLECTION
    if not name or len(name) < 3:
        raise ValueError(f"CHROMA_COLLECTION must be >=3 chars. Got: {name!r}")
    # DO NOT pass embedding_function here (avoids .name() checks in Chroma 1.x)
    try:
        return client.get_or_create_collection(name=name)
    except Exception:
        try:
            return client.get_collection(name=name)
        except Exception:
            return client.create_collection(name=name)


def _embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed documents client-side."""
    emb = get_embeddings()  # your provider-agnostic EF (Cohere/OpenAI/Default)
    # Prefer a batched method; util.llm exposes embed_documents(list[str])
    return emb.embed_documents(texts)


# -------------------- PDF EXTRACTION --------------------
def _extract_text_from_pdf(path: str) -> str:
    """
    Prefer PyMuPDF (fitz) for speed/quality; fallback to pypdf (pure-Python).
    """
    try:
        import fitz  # PyMuPDF
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception:
        from pypdf import PdfReader
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)


# -------------------- INGEST FUNCS --------------------
def ingest_pdfs(paths: List[str]) -> int:
    """
    Ingest a list of PDF file paths into the collection.
    Returns the number of chunks added.
    """
    if not paths:
        return 0
    client = _get_chroma_client()
    kb = _ensure_collection(client, COLLECTION)

    docs, ids, metas = [], [], []
    for path in paths:
        text = _extract_text_from_pdf(path)
        base = os.path.basename(path)
        for i, chunk in enumerate(simple_chunk(text)):
            docs.append(chunk)
            ids.append(f"{base}::{i}")
            metas.append({"source": path, "type": "pdf"})
    if not docs:
        return 0

    vectors = _embed_texts(docs)
    kb.add(documents=docs, metadatas=metas, ids=ids, embeddings=vectors)
    return len(docs)


def ingest_text_blobs(items: List[Dict]) -> int:
    """
    items: [{ "text": "...", "source": "url-or-note" }]
    Returns the number of chunks added.
    """
    if not items:
        return 0
    client = _get_chroma_client()
    kb = _ensure_collection(client, COLLECTION)

    docs, ids, metas = [], [], []
    for i, it in enumerate(items):
        text = (it or {}).get("text", "")
        source = (it or {}).get("source", "ad-hoc")
        if not text:
            continue
        for j, chunk in enumerate(simple_chunk(text)):
            docs.append(chunk)
            ids.append(f"{i}::{j}")
            metas.append({"source": source, "type": "text"})
    if not docs:
        return 0

    vectors = _embed_texts(docs)
    kb.add(documents=docs, metadatas=metas, ids=ids, embeddings=vectors)
    return len(docs)


def ingest_from_urls(urls: List[str]) -> int:
    """
    Given a list of URLs, fetch HTML, convert to markdown, chunk, embed.
    Returns the number of chunks added.
    """
    if not urls:
        return 0
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md

    client = _get_chroma_client()
    kb = _ensure_collection(client, COLLECTION)

    docs, ids, metas = [], [], []
    for i, url in enumerate(urls):
        if not url:
            continue
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            text = md(str(soup), strip=["script", "style"])
            for j, chunk in enumerate(simple_chunk(text)):
                docs.append(chunk)
                ids.append(f"url::{i}::{j}")
                metas.append({"source": url, "type": "url"})
        except Exception:
            # Skip unreachable URL but keep going
            continue
    if not docs:
        return 0

    vectors = _embed_texts(docs)
    kb.add(documents=docs, metadatas=metas, ids=ids, embeddings=vectors)
    return len(docs)


# -------------------- CLI / MAIN --------------------
def _gather_pdfs_from_dir(pdf_dir: Optional[str]) -> List[str]:
    if not pdf_dir:
        return []
    if not os.path.isdir(pdf_dir):
        return []
    # non-recursive: *.pdf under the folder
    return [
        os.path.join(pdf_dir, f)
        for f in os.listdir(pdf_dir)
        if f.lower().endswith(".pdf")
    ]


def _read_jsonl(path: str) -> List[Dict]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = (line or "").strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                # ignore bad lines
                pass
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Ingest PDFs and/or URL/text JSONL into Chroma (client-side embeddings)."
    )
    parser.add_argument("--pdf-dir", default=None, help="Folder containing PDFs (non-recursive)")
    parser.add_argument("--url-file", default=None,
                        help="JSONL file with either {'url': '...'} lines, or {'text': '...', 'source': '...'} lines")
    parser.add_argument("--heartbeat", action="store_true",
                        help="For CHROMA_MODE=http, ping server before ingest")
    parser.add_argument("--collection", default=None,
                        help="Override CHROMA_COLLECTION for this run")

    args = parser.parse_args()

    # Print resolved config
    coll = args.collection or COLLECTION
    print(f"[cfg] MODE={CHROMA_MODE}  HOST={CHROMA_HOST}:{CHROMA_PORT}  TENANT={CHROMA_TENANT}  DB={CHROMA_DATABASE}")
    print(f"[cfg] COLLECTION={coll}  INDEX_DIR={INDEX_DIR}  TELEMETRY={os.getenv('CHROMA_TELEMETRY_ENABLED')}")

    # Optional heartbeat (HTTP mode)
    if args.heartbeat and CHROMA_MODE == "http":
        try:
            client = _get_chroma_client()
            hb = client.heartbeat()
            cols = [c.name for c in client.list_collections()]
            print(f"[ok] Heartbeat: {hb}  ExistingCollections={cols}")
        except Exception as e:
            print(f"[warn] Heartbeat failed: {e}")

    # Ingest PDFs
    total_pdf_chunks = 0
    pdfs = _gather_pdfs_from_dir(args.pdf_dir)
    if pdfs:
        print(f"[ingest] PDFs found: {len(pdfs)} → {args.pdf_dir}")
        total_pdf_chunks = ingest_pdfs(pdfs)
        print(f"[ok] PDF chunks added: {total_pdf_chunks}")
    else:
        print("[skip] No PDFs to ingest")

    # Ingest URL/TEXT JSONL
    total_text_chunks = 0
    total_url_chunks = 0
    if args.url_file and os.path.isfile(args.url_file):
        items = _read_jsonl(args.url_file)
        url_list = [it.get("url") for it in items if isinstance(it, dict) and it.get("url")]
        text_items = [it for it in items if isinstance(it, dict) and it.get("text")]

        if url_list:
            print(f"[ingest] URLs found in JSONL: {len(url_list)}")
            total_url_chunks = ingest_from_urls(url_list)
            print(f"[ok] URL chunks added: {total_url_chunks}")
        if text_items:
            print(f"[ingest] TEXT items found in JSONL: {len(text_items)}")
            total_text_chunks = ingest_text_blobs(text_items)
            print(f"[ok] TEXT chunks added: {total_text_chunks}")
        if not url_list and not text_items:
            print("[skip] JSONL had no usable 'url' or 'text' entries")
    else:
        print("[skip] No --url-file provided or path not found")

    # Summary
    print("\n=== Ingest Summary ===")
    print(f"PDF chunks:  {total_pdf_chunks}")
    print(f"URL chunks:  {total_url_chunks}")
    print(f"TEXT chunks: {total_text_chunks}")
    print("Done.")


if __name__ == "__main__":
    main()
