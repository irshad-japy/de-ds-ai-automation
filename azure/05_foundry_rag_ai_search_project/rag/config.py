from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _int(name: str, default: int) -> int:
    value = os.getenv(name, str(default)).strip()
    return int(value)


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    search_auth_mode: str = os.getenv("SEARCH_AUTH_MODE", "key").strip().lower()
    azure_search_endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT", "").strip().rstrip("/")
    azure_search_admin_key: str = os.getenv("AZURE_SEARCH_ADMIN_KEY", "").strip()
    azure_search_index_name: str = os.getenv("AZURE_SEARCH_INDEX_NAME", "poc05-rag-index").strip()

    foundry_auth_mode: str = os.getenv("FOUNDRY_AUTH_MODE", "key").strip().lower()
    foundry_openai_base_url: str = os.getenv("FOUNDRY_OPENAI_BASE_URL", "").strip()
    foundry_api_key: str = os.getenv("FOUNDRY_API_KEY", "").strip()
    foundry_chat_deployment: str = os.getenv("FOUNDRY_CHAT_DEPLOYMENT", "rag-chat").strip()
    foundry_embedding_deployment: str = os.getenv("FOUNDRY_EMBEDDING_DEPLOYMENT", "rag-embedding").strip()
    embedding_dimensions: int = _int("EMBEDDING_DIMENSIONS", 1536)
    embedding_request_dimensions: bool = _bool("EMBEDDING_REQUEST_DIMENSIONS", False)

    chunk_size_tokens: int = _int("CHUNK_SIZE_TOKENS", 300)
    chunk_overlap_tokens: int = _int("CHUNK_OVERLAP_TOKENS", 50)
    top_k: int = _int("TOP_K", 5)
    max_output_tokens: int = _int("MAX_OUTPUT_TOKENS", 500)

    applicationinsights_connection_string: str = os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
    ).strip()
    log_level: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    @property
    def data_dir(self) -> Path:
        return PROJECT_ROOT / "data" / "synthetic_docs"


settings = Settings()
