from __future__ import annotations

import time
from azure.core.exceptions import HttpResponseError

from rag.chunking import chunk_documents
from rag.clients import embed_texts, get_search_client, get_search_index_client
from rag.config import settings
from rag.documents import load_documents
from rag.index_schema import build_index


def main() -> None:
    docs = load_documents(settings.data_dir)
    print(f"Loaded {len(docs)} source documents from {settings.data_dir}.")

    chunks = chunk_documents(
        docs,
        chunk_size=settings.chunk_size_tokens,
        overlap=settings.chunk_overlap_tokens,
    )
    print(
        f"Created {len(chunks)} chunks "
        f"(chunk_size={settings.chunk_size_tokens}, overlap={settings.chunk_overlap_tokens})."
    )

    print("Generating embeddings...")
    started = time.perf_counter()
    vectors = embed_texts([c.content for c in chunks])
    print(f"Embeddings generated in {(time.perf_counter() - started):.2f}s.")

    index_client = get_search_index_client()
    print(f"Creating/updating index '{settings.azure_search_index_name}'...")
    try:
        index_client.create_or_update_index(build_index())
    except HttpResponseError as exc:
        raise SystemExit(
            "Failed to create/update index. If you changed EMBEDDING_DIMENSIONS or vector schema, "
            "delete the old index first with scripts/delete_index.py and rerun ingestion.\n"
            f"Azure error: {exc}"
        ) from exc

    payload = []
    for chunk, vector in zip(chunks, vectors):
        payload.append(
            {
                "id": chunk.id,
                "title": chunk.title,
                "content": chunk.content,
                "source": chunk.source,
                "category": chunk.category,
                "chunk_id": chunk.chunk_id,
                "effective_date": chunk.effective_date,
                "content_vector": vector,
            }
        )

    search_client = get_search_client()
    print(f"Uploading {len(payload)} chunks...")
    results = search_client.upload_documents(documents=payload)
    succeeded = sum(1 for r in results if r.succeeded)
    failed = [r for r in results if not r.succeeded]
    print(f"Indexed chunks: {succeeded}/{len(results)} succeeded.")

    if failed:
        for r in failed:
            print(f"FAILED key={r.key} error={r.error_message}")
        raise SystemExit(1)

    print("Ingestion completed successfully.")
    print("Next: python -m rag.retrieve --mode vector --query \"What is the return window for damaged items?\"")


if __name__ == "__main__":
    main()
