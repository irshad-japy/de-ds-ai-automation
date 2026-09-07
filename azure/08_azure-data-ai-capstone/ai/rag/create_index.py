from __future__ import annotations

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from common.config import Settings
from common.search_auth import search_admin_credential


def main() -> None:
    s = Settings()
    if not s.search_endpoint:
        raise RuntimeError("Set AZURE_SEARCH_ENDPOINT")
    client = SearchIndexClient(s.search_endpoint, search_admin_credential())
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=s.vector_dimensions,
            vector_search_profile_name="capstone-vector-profile",
        ),
    ]
    vector = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="capstone-hnsw")],
        profiles=[
            VectorSearchProfile(
                name="capstone-vector-profile",
                algorithm_configuration_name="capstone-hnsw",
            )
        ],
    )
    index = SearchIndex(name=s.search_index, fields=fields, vector_search=vector)
    client.create_or_update_index(index)
    print(f"[SUCCESS] Search index ready: {s.search_index}")


if __name__ == "__main__":
    main()
