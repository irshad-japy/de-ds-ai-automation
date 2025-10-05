import time, uuid, os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from .embedder import embed_texts

COLLECTION = "ai_kb"

def qdrant():
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    return QdrantClient(url=url)

def ensure_collection():
    client = qdrant()
    has = client.collection_exists(COLLECTION)
    if not has:
        client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE) # MiniLM-L6-v2 size
        )

def chunk_text(doc_id: str, text: str, poc_key: str, md: Dict[str, Any], target_tokens=800):
    # simple line-based chunking
    lines = text.splitlines()
    chunks, buf, n = [], [], 0
    for ln in lines:
        buf.append(ln)
        n += max(1, len(ln)//8)  # rough token-ish
        if n >= target_tokens:
            chunks.append("\n".join(buf))
            buf, n = [], 0
    if buf: chunks.append("\n".join(buf))
    out = []
    ts = int(time.time())
    for i, ch in enumerate(chunks):
        out.append({
            "id": str(uuid.uuid4()),
            "payload": {
                "poc_key": poc_key, "doc_id": doc_id, "chunk_index": i,
                **(md or {}), "created_at": ts
            },
            "text": ch
        })
    return out

def ingest_docs(poc_key: str, docs: List[Dict[str,str]], metadata: Dict[str,Any]):
    ensure_collection()
    client = qdrant()
    prepared = []
    for d in docs:
        prepared.extend(chunk_text(d["doc_id"], d["text"], poc_key, metadata))
    vectors = embed_texts([p["text"] for p in prepared])
    points = [
        PointStruct(id=p["id"], vector=vectors[i].tolist(), payload=p["payload"])
        for i,p in enumerate(prepared)
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    return prepared

def search(query: str, filters: Dict[str,Any], top_k=6):
    ensure_collection()
    client = qdrant()
    flt = None
    if filters:
        conds = []
        for k,v in filters.items():
            conds.append(FieldCondition(key=k, match=MatchValue(value=v)))
        flt = Filter(must=conds)
    qvec = embed_texts([query])[0].tolist()
    res = client.search(collection_name=COLLECTION, query_vector=qvec, limit=top_k, query_filter=flt)
    return res
