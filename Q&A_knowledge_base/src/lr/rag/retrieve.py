from rapidfuzz import fuzz
from ..vector.qdrant_store import ensure_collection, upsert, search
from .embedder import get_embedder
import os, uuid

def index_texts(pairs: list[tuple[str, str]]):
    emb = get_embedder()
    texts = [t for _, t in pairs]
    vecs = emb.embed(texts)
    if not vecs or not vecs[0]:
        raise RuntimeError("Embedding model returned zero-length vectors.")
    dim = len(vecs[0])
    ensure_collection(dim)

    payloads, ids = [], []
    for key, text in pairs:
        # key like "filename.ext::0" (your reader does this)
        source, _, chunk_idx = key.partition("::")
        ext = os.path.splitext(source)[1].lower()  # ".pdf", ".md", ".txt", ".csv", ...
        payloads.append({
            "text": text,
            "source": source,
            "chunk": int(chunk_idx or 0),
            "ext": ext,
        })
        ids.append(str(uuid.uuid5(uuid.NAMESPACE_URL, key)))

    upsert(vecs, payloads=payloads, ids=ids)
    return {"chunks_indexed": len(ids)}

def retrieve(query: str, k: int = 6, only_ext: str | None = None, min_score: float = 0.25):
    emb = get_embedder()
    q = emb.embed([query])[0]

    # get generous candidates (3x), then filter
    hits = search(q, top_k=k * 6, score_threshold=min_score)

    # optional: only certain file types (e.g., PDFs)
    if only_ext:
        only_ext = only_ext.lower()
        hits = [(i,s,pl) for (i,s,pl) in hits if pl.get("ext","").lower() == only_ext]

    # now re-rank by semantic + fuzzy signal (simple heuristic)
    def keyfn(t):
        _id, _score, pl = t
        text = pl.get("text","")
        return (0.6 * _score) + (0.4 * (fuzz.token_set_ratio(query, text) / 100.0))

    hits = sorted(hits, key=keyfn, reverse=True)[:k]

    # return both plain texts and metadata (up to you)
    return hits  # list of (id, score, payload)
