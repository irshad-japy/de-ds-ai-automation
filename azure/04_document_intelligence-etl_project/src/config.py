from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}

@dataclass(frozen=True)
class Settings:
    storage_account_name: str
    storage_container: str
    document_intelligence_endpoint: str
    document_intelligence_api_key: str | None
    azure_sql_connection_string: str | None
    critical_confidence_threshold: float
    amount_tolerance: float
    enable_sql_load: bool

    @property
    def storage_account_url(self) -> str:
        return f"https://{self.storage_account_name}.blob.core.windows.net"

def get_settings() -> Settings:
    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "").strip()
    endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT", "").strip()

    if not storage_account_name:
        raise RuntimeError("AZURE_STORAGE_ACCOUNT_NAME is required.")
    if not endpoint:
        raise RuntimeError("DOCUMENTINTELLIGENCE_ENDPOINT is required.")

    return Settings(
        storage_account_name=storage_account_name,
        storage_container=os.getenv("AZURE_STORAGE_CONTAINER", "documents").strip() or "documents",
        document_intelligence_endpoint=endpoint,
        document_intelligence_api_key=os.getenv("DOCUMENTINTELLIGENCE_API_KEY", "").strip() or None,
        azure_sql_connection_string=os.getenv("AZURE_SQL_CONNECTIONSTRING", "").strip() or None,
        critical_confidence_threshold=float(os.getenv("CRITICAL_CONFIDENCE_THRESHOLD", "0.70")),
        amount_tolerance=float(os.getenv("AMOUNT_TOLERANCE", "0.05")),
        enable_sql_load=_as_bool(os.getenv("ENABLE_SQL_LOAD"), True),
    )
