from __future__ import annotations

from azure.identity import get_bearer_token_provider
from openai import OpenAI

from common.auth import get_token_credential
from common.config import Settings


def get_embedding_client() -> OpenAI:
    s = Settings()
    if not s.openai_endpoint:
        raise RuntimeError("Set AZURE_OPENAI_ENDPOINT in .env")
    base_url = s.openai_endpoint.rstrip("/") + "/openai/v1/"
    if s.openai_api_key:
        return OpenAI(base_url=base_url, api_key=s.openai_api_key)
    token_provider = get_bearer_token_provider(
        get_token_credential(), "https://cognitiveservices.azure.com/.default"
    )
    return OpenAI(base_url=base_url, api_key=token_provider)


def embed_text(text: str) -> list[float]:
    s = Settings()
    client = get_embedding_client()
    result = client.embeddings.create(model=s.embedding_deployment, input=text)
    return list(result.data[0].embedding)
