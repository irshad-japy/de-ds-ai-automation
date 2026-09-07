from __future__ import annotations

import argparse

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from common.config import Settings
from common.embeddings import embed_text
from common.search_auth import search_query_credential


def retrieve(question: str, top: int = 3) -> list[dict]:
    s = Settings()
    vector = embed_text(question)
    query = VectorizedQuery(vector=vector, k_nearest_neighbors=max(top, 3), fields="content_vector")
    client = SearchClient(s.search_endpoint, s.search_index, search_query_credential())
    results = client.search(
        search_text=question,
        vector_queries=[query],
        select=["id", "title", "content", "source", "category"],
        top=top,
    )
    return [dict(r) for r in results]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", default="When is a shipment considered delayed?")
    parser.add_argument("--top", type=int, default=3)
    args = parser.parse_args()
    rows = retrieve(args.question, args.top)
    for i, row in enumerate(rows, 1):
        print(f"\n#{i} {row.get('title')} [{row.get('source')}]")
        print(row.get("content"))
    if not rows:
        raise RuntimeError("No search results returned")
    print("\n[SUCCESS] Hybrid/vector retrieval returned grounded sources.")


if __name__ == "__main__":
    main()
