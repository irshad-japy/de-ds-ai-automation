"""
python -m src.tools.chromadb_poc
"""

# python -m src.tools.chromadb_poc

import os
import time
import chromadb

HOST = os.getenv("CHROMA_HOST", "localhost")
PORT = int(os.getenv("CHROMA_PORT", "8000"))

# Connect to Dockerized Chroma
client = chromadb.HttpClient(host=HOST, port=PORT)

# Wait briefly for server to be ready
for _ in range(20):
    try:
        client.list_collections()
        break
    except Exception:
        time.sleep(0.2)

COL_NAME = "smoke_test_v1"

# Clean old collection (ignore errors)
try:
    client.delete_collection(COL_NAME)
except Exception:
    pass

col = client.get_or_create_collection(name=COL_NAME)

# Tiny dataset
docs = ["pineapple doc", "orange doc", "banana doc"]
ids  = ["d1", "d2", "d3"]

# 4-d test embeddings (any consistent length works)
embs = [
    [0.10, 0.20, 0.30, 0.40],
    [0.20, 0.10, 0.40, 0.30],
    [0.90, 0.10, 0.00, 0.20],
]

# Upsert WITH embeddings (prevents local ONNX usage)
col.upsert(ids=ids, documents=docs, embeddings=embs)

# Query with an embedding of the same dimension
q_emb = [[0.15, 0.15, 0.35, 0.35]]

res = col.query(
    query_embeddings=q_emb,
    n_results=2,
    include=["documents", "distances"],  # ✅ no "ids" here
)

print("OK — Chroma responded.")
print("IDs:", res["ids"][0])             # IDs are always present
print("Docs:", res["documents"][0])
print("Distances:", res["distances"][0])
