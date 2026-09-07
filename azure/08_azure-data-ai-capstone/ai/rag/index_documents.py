from __future__ import annotations

import json
from pathlib import Path

from azure.search.documents import SearchClient

from common.config import Settings
from common.embeddings import embed_text
from common.search_auth import search_admin_credential


def main() -> None:
    s = Settings()
    docs = json.loads(Path("output/search/documents.json").read_text(encoding="utf-8"))
    for doc in docs:
        doc["content_vector"] = embed_text(doc["content"])
        if len(doc["content_vector"]) != s.vector_dimensions:
            raise RuntimeError(
                f"Embedding dimensions {len(doc['content_vector'])} != SEARCH_VECTOR_DIMENSIONS {s.vector_dimensions}"
            )
    client = SearchClient(s.search_endpoint, s.search_index, search_admin_credential())
    result = client.upload_documents(docs)
    failed = [r for r in result if not r.succeeded]
    if failed:
        raise RuntimeError(f"Search upload failed for {len(failed)} document(s): {failed}")
    print(f"[SUCCESS] Indexed {len(docs)} documents")


if __name__ == "__main__":
    main()
