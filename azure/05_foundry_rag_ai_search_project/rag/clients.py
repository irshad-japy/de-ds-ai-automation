from __future__ import annotations

from typing import Iterable

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from openai import OpenAI

from rag.config import settings


def _validate_auth_mode(value: str, label: str) -> None:
    if value not in {"key", "entra"}:
        raise ValueError(f"{label} must be either 'key' or 'entra', got: {value!r}")


def get_search_credential():
    _validate_auth_mode(settings.search_auth_mode, "SEARCH_AUTH_MODE")
    if settings.search_auth_mode == "key":
        if not settings.azure_search_admin_key:
            raise ValueError("AZURE_SEARCH_ADMIN_KEY is required when SEARCH_AUTH_MODE=key")
        return AzureKeyCredential(settings.azure_search_admin_key)
    return DefaultAzureCredential()


def get_search_index_client() -> SearchIndexClient:
    if not settings.azure_search_endpoint:
        raise ValueError("AZURE_SEARCH_ENDPOINT is missing")
    return SearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=get_search_credential(),
    )


def get_search_client() -> SearchClient:
    if not settings.azure_search_endpoint:
        raise ValueError("AZURE_SEARCH_ENDPOINT is missing")
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=get_search_credential(),
    )


def get_foundry_client() -> OpenAI:
    _validate_auth_mode(settings.foundry_auth_mode, "FOUNDRY_AUTH_MODE")
    if not settings.foundry_openai_base_url:
        raise ValueError("FOUNDRY_OPENAI_BASE_URL is missing")

    base_url = settings.foundry_openai_base_url
    if not base_url.endswith("/"):
        base_url += "/"

    if settings.foundry_auth_mode == "key":
        if not settings.foundry_api_key:
            raise ValueError("FOUNDRY_API_KEY is required when FOUNDRY_AUTH_MODE=key")
        return OpenAI(base_url=base_url, api_key=settings.foundry_api_key)

    # Microsoft Foundry/OpenAI-compatible v1 endpoints support Microsoft Entra ID.
    # Azure CLI login is picked up by DefaultAzureCredential for local development.
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default",
    )
    return OpenAI(base_url=base_url, api_key=token_provider)


def embed_texts(texts: Iterable[str]) -> list[list[float]]:
    items = list(texts)
    if not items:
        return []

    client = get_foundry_client()
    kwargs = {
        "model": settings.foundry_embedding_deployment,
        "input": items,
    }
    if settings.embedding_request_dimensions:
        kwargs["dimensions"] = settings.embedding_dimensions

    response = client.embeddings.create(**kwargs)
    vectors = [row.embedding for row in response.data]

    for i, vector in enumerate(vectors):
        if len(vector) != settings.embedding_dimensions:
            raise ValueError(
                "Embedding dimension mismatch for item "
                f"{i}: model returned {len(vector)}, but EMBEDDING_DIMENSIONS="
                f"{settings.embedding_dimensions}. Update .env and recreate the index."
            )
    return vectors


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
