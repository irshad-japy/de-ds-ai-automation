"""
python test_main.py
"""

import os
import re
import uuid
import yaml
import requests
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


# ---------------- Qdrant ----------------
client = QdrantClient(url="http://localhost:6333", prefer_grpc=False, timeout=30.0,)

COLLECTION = "local_rag_chunks"
embedings_MODEL = "mxbai-embedings-large"      # 1024 dims
GEN_MODEL = "gemma3:12b-it-qat"        # adjust to your local model name

# Create collection if not present
if not client.collection_exists(collection_name=COLLECTION):
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

# --------------- Utilities ---------------
def extract_metadata_from_mdx(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    parts = content.split('---')
    if len(parts) < 3:
        return {}, content

    raw_metadata = parts[1]
    article_content = '---'.join(parts[2:]).strip()

    try:
        metadata = yaml.safe_load(raw_metadata)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML metadata: {e}")
        return {}, article_content

    return metadata, article_content


def clean_article_content(text: str) -> str:
    # Keep it minimal for PDFs; remove html-like tags and collapse whitespace
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def create_chunks(text: str, chunk_size: int = 1200, overlap: int = 200):
    """
    Word-based sliding window chunking for more even chunks from PDFs.
    """
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(words):
        end = min(len(words), start + chunk_size)
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start += step
    return chunks


def generate_response(prompt: str) -> str:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": GEN_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_ctx": 10000}
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.json().get("response", "")


def parse_embedings_response(j):
    """
    Ollama /api/embedings returns either:
      {"data": [{"embedings": [...]}]}   (newer)
    or
      {"embedings": [[...]]}            (older)
    """
    if isinstance(j, dict) and "data" in j:
        return j["data"][0]["embedings"]
    return j["embedings"][0]


def generate_embedings(text: str):
    r = requests.post(
        "http://localhost:11434/api/embedings",
        json={"model": embedings_MODEL, "input": text},
        timeout=120,
    )
    r.raise_for_status()
    j = r.json()
    emb = parse_embedings_response(j)
    # emb must be a list[float] of length 1024
    return emb


def store_article(metadata: dict, chunks: list[str]):
    points = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        emb = generate_embedings(chunk)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={**metadata, "content": chunk, "chunk_id": i},
            )
        )
    if points:
        client.upsert(collection_name=COLLECTION, wait=True, points=points)


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        texts.append(page_text)
    return "\n".join(texts).strip()

# ----------------- Main ------------------
def main():
    # 1) Ingest PDFs from ./input
    pdf_files = [f for f in os.listdir("input") if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("No PDFs found in ./input")

    for pdf_file in pdf_files:
        file_path = os.path.join("input", pdf_file)
        raw_text = extract_text_from_pdf(file_path)
        if not raw_text:
            print(f"Warning: No extractable text in {pdf_file} (maybe scanned image?).")
            continue

        cleaned = clean_article_content(raw_text)
        chunks = create_chunks(cleaned)

        slug = os.path.splitext(pdf_file)[0]
        metadata = {
            "title": slug.replace("_", " ").replace("-", " ").title(),
            "slug": slug,
            "source_type": "pdf",
            "source_path": file_path,
        }

        store_article(metadata=metadata, chunks=chunks)
        print(f"Ingested: {pdf_file} (chunks: {len(chunks)})")

    # 2) Query
    prompt = input("Enter a prompt: ").strip()
    adjusted_prompt = f"Represent this sentence for searching relevant passages: {prompt}"

    emb_res = requests.post(
        "http://localhost:11434/api/embedings",
        json={"model": embedings_MODEL, "input": adjusted_prompt},
        timeout=120,
    )
    emb_res.raise_for_status()
    query_vec = parse_embedings_response(emb_res.json())

    results = client.query_points(
        collection_name=COLLECTION,
        query=query_vec,
        with_payload=True,
        limit=10,
    )

    relevant_passages = "\n".join([
        f"- Article Title: {pt.payload.get('title','')} -- "
        f"Article Slug: {pt.payload.get('slug','')} -- "
        f"Article Content: {pt.payload.get('content','')}"
        for pt in getattr(results, "points", [])
        if getattr(pt, "payload", None)
    ])

    augmented_prompt = f"""
The following are relevant passages:
<retrieved-data>
{relevant_passages}
</retrieved-data>

Here's the original user prompt, answer with help of the retrieved passages:
<user-prompt>
{prompt}
</user-prompt>
"""

    answer = generate_response(augmented_prompt)
    print("\n--- Answer ---\n")
    print(answer)


if __name__ == "__main__":
    main()
