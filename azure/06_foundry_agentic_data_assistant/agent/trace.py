from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
TRACE_FILE = LOG_DIR / "agent_trace.jsonl"


def configure_logging() -> None:
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")
    conn = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "").strip()
    if conn:
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor
            configure_azure_monitor(connection_string=conn)
            logging.info("Application Insights/OpenTelemetry configured")
        except Exception as exc:
            logging.warning("Application Insights setup skipped: %s", exc)


def _redact(value: Any) -> Any:
    secret_words = {"key", "token", "secret", "password", "connection_string", "authorization"}
    if isinstance(value, dict):
        return {k: ("***REDACTED***" if any(w in k.lower() for w in secret_words) else _redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    return value


def write_trace(event: str, payload: dict[str, Any]) -> None:
    record = {"ts_epoch": round(time.time(), 3), "event": event, **_redact(payload)}
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
