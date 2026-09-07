from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import PurePosixPath

from .config import Settings
from .extract_invoice import analyze_invoice_bytes
from .sql_loader import invoice_exists, upsert_invoice
from .storage_client import StorageRepository
from .validate_invoice import validate_invoice

class InvoicePipeline:
    def __init__(self, settings: Settings, storage: StorageRepository | None = None):
        self.settings = settings
        self.storage = storage or StorageRepository(settings)

    @staticmethod
    def source_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _safe_name(source_blob: str) -> str:
        name = PurePosixPath(source_blob).name
        return name.rsplit(".", 1)[0]

    def process_blob(self, source_blob: str) -> dict:
        data = self.storage.download_bytes(source_blob)
        return self.process_bytes(data, source_blob)

    def process_bytes(self, data: bytes, source_blob: str) -> dict:
        started = time.perf_counter()
        digest = self.source_hash(data)
        stem = self._safe_name(source_blob)
        processed_marker = f"processed/{stem}.{digest[:12]}.json"
        failure_marker = f"failed/{stem}.{digest[:12]}.failure.json"
        raw_marker = f"processed/raw/{stem}.{digest[:12]}.raw.json"

        # First idempotency guard: already completed or quarantined in storage.
        if self.storage.exists(processed_marker):
            return {
                "status": "skipped_duplicate",
                "source_blob": source_blob,
                "source_hash": digest,
                "processed_marker": processed_marker,
            }
        if self.storage.exists(failure_marker):
            return {
                "status": "skipped_duplicate_failed",
                "source_blob": source_blob,
                "source_hash": digest,
                "failure_marker": failure_marker,
            }

        # Second idempotency guard: already present in SQL.
        if (
            self.settings.enable_sql_load
            and self.settings.azure_sql_connection_string
            and invoice_exists(self.settings.azure_sql_connection_string, digest)
        ):
            return {
                "status": "skipped_duplicate_sql",
                "source_blob": source_blob,
                "source_hash": digest,
            }

        try:
            raw, normalized = analyze_invoice_bytes(data, self.settings)
            self.storage.upload_json(raw_marker, raw)

            validation = validate_invoice(
                normalized,
                confidence_threshold=self.settings.critical_confidence_threshold,
                tolerance=self.settings.amount_tolerance,
            )

            normalized["source"] = {
                "blob_name": source_blob,
                "sha256": digest,
                "processed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            normalized["validation"] = validation.to_dict()

            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            normalized["telemetry"] = {
                "processing_latency_ms": elapsed_ms,
                "low_confidence_field_count": len(validation.low_confidence_fields),
            }

            if not validation.is_valid:
                failure_payload = {
                    "status": "failed_validation",
                    "source_blob": source_blob,
                    "source_hash": digest,
                    "failure_reason": validation.errors,
                    "warnings": validation.warnings,
                    "normalized_invoice": normalized,
                }
                self.storage.upload_json(failure_marker, failure_payload)
                return failure_payload

            if self.settings.enable_sql_load:
                if not self.settings.azure_sql_connection_string:
                    raise RuntimeError(
                        "ENABLE_SQL_LOAD=true but AZURE_SQL_CONNECTIONSTRING is empty. "
                        "Either configure Azure SQL or set ENABLE_SQL_LOAD=false for extraction-only testing."
                    )
                upsert_invoice(
                    self.settings.azure_sql_connection_string,
                    normalized,
                    source_blob=source_blob,
                    source_hash=digest,
                )

            self.storage.upload_json(processed_marker, normalized)
            return {
                "status": "processed",
                "source_blob": source_blob,
                "source_hash": digest,
                "processed_marker": processed_marker,
                "latency_ms": elapsed_ms,
            }

        except Exception as exc:
            failure_payload = {
                "status": "failed_exception",
                "source_blob": source_blob,
                "source_hash": digest,
                "failure_reason": [f"{type(exc).__name__}: {exc}"],
            }
            self.storage.upload_json(failure_marker, failure_payload)
            raise
