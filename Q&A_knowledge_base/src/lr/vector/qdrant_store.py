from typing import Iterable, List, Dict, Any, Optional, Tuple, Union
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter
from ..config import settings  # <- use .env

client = QdrantClient(
    url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
    prefer_grpc=False,
    timeout=30.0,
)
COLLECTION_NAME = settings.qdrant_collection

def ensure_collection(dim: int) -> None:
    # If exists, verify dim; recreate if different
    try:
        info = client.get_collection(collection_name=COLLECTION_NAME)
        # Qdrant 1.9+ exposes config like this:
        current_dim = None
        params = getattr(info, "config", None) and getattr(info.config, "params", None)
        vectors = params and getattr(params, "vectors", None)
        if hasattr(vectors, "size"):
            current_dim = vectors.size  # single-vector collection
        elif isinstance(vectors, dict) and "size" in vectors:
            current_dim = vectors["size"]

        if current_dim == dim:
            return

        # Dimension mismatch -> recreate
        client.delete_collection(collection_name=COLLECTION_NAME)
    except Exception:
        # Not existing or cannot read -> create fresh
        pass

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

def _to_list(vec):
    try:
        import numpy as np  # type: ignore
        if hasattr(vec, "tolist"):
            return vec.tolist()
    except Exception:
        pass
    return list(vec)

def upsert(
    points_or_vectors: Iterable,
    payloads: Optional[Iterable[Dict[str, Any]]] = None,
    ids: Optional[Iterable[Union[int, str]]] = None,
    batch_size: int = 512,
):
    """
    Supports:
      A) upsert([{"id": "...", "vector": [...], "payload": {...}}, ...])
      B) upsert(vectors=[...], payloads=[...], ids=[...])
    """
    # Mode A: list of point dicts
    if payloads is None and (
        isinstance(points_or_vectors, list)
        or hasattr(points_or_vectors, "__iter__")
    ) and points_or_vectors and isinstance(next(iter(points_or_vectors)), dict):
        vectors: List[List[float]] = []
        pls: List[Dict[str, Any]] = []
        id_list: List[Optional[Union[int, str]]] = []

        for p in points_or_vectors:
            vec = p.get("vector") or p.get("embedding") or p.get("values")
            if vec is None:
                raise ValueError("Point missing 'vector'/'embedding'/'values'.")
            vectors.append(_to_list(vec))
            pl = p.get("payload") or {k: v for k, v in p.items() if k not in ("id", "vector", "embedding", "values")}
            pls.append(pl or {})
            id_list.append(p.get("id"))
        _upsert_batches(vectors, pls, id_list, batch_size=batch_size)
        return

    # Mode B: vectors/payloads/ids
    if payloads is None:
        raise TypeError("upsert() missing required 'payloads' when not passing point dicts.")

    vec_list = [_to_list(v) for v in points_or_vectors]
    pl_list = list(payloads)
    if ids is None:
        id_list = [None] * len(vec_list)
    else:
        id_list = list(ids)
        if len(id_list) != len(vec_list):
            raise ValueError("Length of ids must match vectors/payloads.")
    if len(pl_list) != len(vec_list):
        raise ValueError("Length of payloads must match vectors.")

    _upsert_batches(vec_list, pl_list, id_list, batch_size=batch_size)

def _upsert_batches(
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
    ids: List[Optional[Union[int, str]]],
    batch_size: int = 512,
) -> None:
    n = len(vectors)
    for i in range(0, n, batch_size):
        chunk = []
        for vec, pl, pid in zip(vectors[i:i+batch_size], payloads[i:i+batch_size], ids[i:i+batch_size]):
            point = {"vector": vec, "payload": pl}
            if pid is not None:
                point["id"] = pid
            chunk.append(point)
        client.upsert(collection_name=COLLECTION_NAME, points=chunk)

def search(
    query_vector: Union[List[float], Tuple[float, ...]],
    top_k: int = 12,
    score_threshold: Optional[float] = None,
    query_filter: Optional[Filter] = None,
):
    try:
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()
    except Exception:
        query_vector = list(query_vector)

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        score_threshold=score_threshold,
        query_filter=query_filter,
    )
    return [(r.id, float(r.score), dict(r.payload or {})) for r in results]
