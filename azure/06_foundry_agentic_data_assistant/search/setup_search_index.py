from __future__ import annotations

import json
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchableField, SearchFieldDataType, SearchIndex, SimpleField
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main():
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
    index_name = os.getenv("SEARCH_INDEX_NAME", "poc06-policy-index")
    credential = AzureKeyCredential(key)

    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, searchable=True),
        SearchableField(name="content", type=SearchFieldDataType.String, searchable=True),
        SimpleField(name="url", type=SearchFieldDataType.String, filterable=False),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
    ]
    index = SearchIndex(name=index_name, fields=fields)
    index_client.create_or_update_index(index)
    print(f"[SUCCESS] Search index ready: {index_name}")

    docs = json.loads((ROOT / "data" / "policies.json").read_text(encoding="utf-8"))
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    results = search_client.upload_documents(docs)
    failed = [r for r in results if not r.succeeded]
    if failed:
        raise RuntimeError(f"Upload failures: {failed}")
    print(f"[SUCCESS] Uploaded {len(results)} policy documents")


if __name__ == "__main__":
    main()
