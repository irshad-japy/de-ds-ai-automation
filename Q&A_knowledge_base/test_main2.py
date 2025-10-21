"""
python test_main2.py
"""

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import re
import os
import uuid
from typing import List, Dict, Any

try:
    from PyPDF2 import PdfReader
except ImportError:
    raise SystemExit("Please install PyPDF2: pip install PyPDF2")

# --- Config ---
QDRANT_URL = "http://localhost:6333"
OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "mxbai-embed-large"   # 1024-dim
GEN_MODEL = "gemma3:12b-it-qat"     # change if you use another local model
COLLECTION = "articles"

PDF_PATH = "input/rustdesk_ec2_setup_using_docker_guide_.pdf"  # << your file
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

# --- Qdrant setup ---
client = QdrantClient(url=QDRANT_URL)
if not client.collection_exists(collection_name=COLLECTION):
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

# --- Helpers ---
def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    parts = []
    for page in reader.pages:
        parts.append((page.extract_text() or ""))
    return "\n".join(parts).strip()

def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    reader = PdfReader(file_path)
    info = reader.metadata or {}
    title = (getattr(info, "title", None) or info.get("/Title")
             or os.path.splitext(os.path.basename(file_path))[0])
    author = (getattr(info, "author", None) or info.get("/Author") or "")
    subject = (getattr(info, "subject", None) or info.get("/Subject") or "")
    keywords = (getattr(info, "keywords", None) or info.get("/Keywords") or "")
    return {
        "title": str(title),
        "author": str(author),
        "subject": str(subject),
        "keywords": str(keywords),
        "filename": os.path.basename(file_path),
    }

def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def create_chunks_from_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    if not text:
        return []
    chunks, n = [], len(text)
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks

def _extract_embedding(json_obj: Dict[str, Any]):
    # /api/embed may return "embedding" (string) or "embeddings" (list)
    if "embedding" in json_obj:
        return json_obj["embedding"]
    if "embeddings" in json_obj and json_obj["embeddings"]:
        return json_obj["embeddings"][0]
    return None

def generate_embeddings(text: str):
    r = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=120,
    )
    r.raise_for_status()
    return _extract_embedding(r.json())

def generate_response(prompt: str) -> str:
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": GEN_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_ctx": 10000},
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()

def store_article(metadata: dict, chunks: List[str]):
    for idx, chunk in enumerate(chunks):
        emb = generate_embeddings(chunk)
        if emb is None:
            continue
        point_id = str(uuid.uuid4())
        payload = {**metadata, "content": chunk, "chunk_index": idx}
        client.upsert(
            collection_name=COLLECTION,
            wait=True,
            points=[PointStruct(id=point_id, vector=emb, payload=payload)],
        )

# --- Main ---
def main():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    # 1) Ingest the single PDF
    meta = extract_pdf_metadata(PDF_PATH)
    text = extract_text_from_pdf(PDF_PATH)
    cleaned = clean_text(text)
    chunks = create_chunks_from_text(cleaned, CHUNK_SIZE, CHUNK_OVERLAP)
    meta["slug"] = os.path.splitext(os.path.basename(PDF_PATH))[0]
    store_article(metadata=meta, chunks=chunks)

    # 2) Query
    prompt = input("Enter a prompt: ").strip()
    adjusted = f"Represent this sentence for searching relevant passages: {prompt}"
    r = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": adjusted},
        timeout=240,
    )
    r.raise_for_status()
    query_emb = _extract_embedding(r.json())
    if query_emb is None:
        print("Failed to get query embedding.")
        return

    results = client.query_points(
        collection_name=COLLECTION,
        query=query_emb,
        with_payload=True,
        limit=20
    )

    relevant_passages = "\n".join([
        f"- Title: {p.payload.get('title','')} | Slug: {p.payload.get('slug','')} | Content: {p.payload.get('content','')}"
        for p in (results.points or [])
    ])

    augmented = f"""
Use the retrieved passages to answer the user's question precisely.
If the passages don't contain the answer, say so briefly.

<retrieved-data>
{relevant_passages}
</retrieved-data>

<user-prompt>
{prompt}
</user-prompt>
"""
    answer = generate_response(augmented)
    print(answer)

if __name__ == "__main__":
    main()
