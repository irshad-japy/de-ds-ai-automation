from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def require(*names: str) -> dict[str, str]:
    missing = [name for name in names if not env(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
            + ". Copy .env.example to .env and fill the required values."
        )
    return {name: env(name) for name in names}


@dataclass(frozen=True)
class Settings:
    auth_mode: str = env("AZURE_AUTH_MODE", "browser")
    tenant_id: str = env("AZURE_TENANT_ID")
    resource_group: str = env("AZURE_RESOURCE_GROUP", "rg-poc08-capstone")
    location: str = env("AZURE_LOCATION", "eastus")

    adls_account_url: str = env("ADLS_ACCOUNT_URL")
    adls_file_system: str = env("ADLS_FILE_SYSTEM", "datalake")
    storage_connection_string: str = env("AZURE_STORAGE_CONNECTION_STRING")

    eventhub_namespace: str = env("EVENTHUB_FULLY_QUALIFIED_NAMESPACE")
    eventhub_name: str = env("EVENTHUB_NAME", "shipment-events")
    eventhub_consumer_group: str = env("EVENTHUB_CONSUMER_GROUP", "$Default")
    eventhub_connection_string: str = env("EVENTHUB_CONNECTION_STRING")

    search_endpoint: str = env("AZURE_SEARCH_ENDPOINT")
    search_index: str = env("AZURE_SEARCH_INDEX", "capstone-knowledge")
    search_admin_key: str = env("AZURE_SEARCH_ADMIN_KEY")
    search_query_key: str = env("AZURE_SEARCH_QUERY_KEY")
    vector_dimensions: int = int(env("SEARCH_VECTOR_DIMENSIONS", "1536"))

    openai_endpoint: str = env("AZURE_OPENAI_ENDPOINT")
    openai_api_key: str = env("AZURE_OPENAI_API_KEY")
    embedding_deployment: str = env(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"
    )

    foundry_project_endpoint: str = env("FOUNDRY_PROJECT_ENDPOINT")
    foundry_model: str = env("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5-mini")
    foundry_agent_name: str = env("FOUNDRY_AGENT_NAME")
