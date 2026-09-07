from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
from typing import Literal

from azure.search.documents.models import VectorizedQuery

from rag.clients import embed_text, get_search_client
from rag.config import settings


@dataclass
class RetrievedChunk:
    score: float
    id: str
    title: str
    content: str
    source: str
    category: str
    chunk_id: str
    effective_date: str

    def to_dict(self) -> dict:
        return asdict(self)


def _escape_odata(value: str) -> str:
    return value.replace("'", "''")


def retrieve(
    query: str,
    mode: Literal["vector", "hybrid"] = "hybrid",
    top_k: int | None = None,
    category: str | None = None,
) -> list[RetrievedChunk]:
    if mode not in {"vector", "hybrid"}:
        raise ValueError("mode must be 'vector' or 'hybrid'")
    top_k = top_k or settings.top_k

    vector = embed_text(query)
    vector_query = VectorizedQuery(
        vector=vector,
        k_nearest_neighbors=top_k,
        fields="content_vector",
        kind="vector",
    )

    filter_expr = None
    if category:
        filter_expr = f"category eq '{_escape_odata(category)}'"

    client = get_search_client()
    kwargs = {
        "vector_queries": [vector_query],
        "select": [
            "id",
            "title",
            "content",
            "source",
            "category",
            "chunk_id",
            "effective_date",
        ],
        "top": top_k,
        "include_total_count": True,
    }
    if filter_expr:
        kwargs["filter"] = filter_expr
    if mode == "hybrid":
        kwargs["search_text"] = query

    results = client.search(**kwargs)
    output: list[RetrievedChunk] = []
    for item in results:
        output.append(
            RetrievedChunk(
                score=float(item.get("@search.score") or 0.0),
                id=item["id"],
                title=item.get("title", ""),
                content=item.get("content", ""),
                source=item.get("source", ""),
                category=item.get("category", ""),
                chunk_id=item.get("chunk_id", ""),
                effective_date=item.get("effective_date", ""),
            )
        )
    return output


def print_results(results: list[RetrievedChunk]) -> None:
    if not results:
        print("No results found.")
        return
    for i, row in enumerate(results, 1):
        preview = " ".join(row.content.split())[:280]
        print(f"\n#{i} score={row.score:.6f}")
        print(f"source={row.source} chunk_id={row.chunk_id} category={row.category}")
        if row.effective_date:
            print(f"effective_date={row.effective_date}")
        print(f"title={row.title}")
        print(f"preview={preview}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Vector or hybrid retrieval against Azure AI Search")
    parser.add_argument("--query", required=True)
    parser.add_argument("--mode", choices=["vector", "hybrid"], default="hybrid")
    parser.add_argument("--top-k", type=int, default=settings.top_k)
    parser.add_argument("--category", default=None)
    args = parser.parse_args()

    rows = retrieve(args.query, args.mode, args.top_k, args.category)
    print_results(rows)


if __name__ == "__main__":
    main()
