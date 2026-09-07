"""Approved read-only tool implementations used by the Foundry function-calling loop.

SECURITY INVARIANT:
- This module does NOT accept SQL text.
- It exposes only four named business operations.
- In FUNCTION mode, each operation calls one fixed Azure Function endpoint.
- In MOCK mode, each operation reads deterministic local JSON for first-success testing.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MOCK_FILE = PROJECT_ROOT / "data" / "mock_business_data.json"


class ToolValidationError(ValueError):
    pass


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except Exception as exc:
        raise ToolValidationError(f"{field_name} must be YYYY-MM-DD") from exc


def _validate_order_id(order_id: int) -> int:
    try:
        value = int(order_id)
    except Exception as exc:
        raise ToolValidationError("order_id must be an integer") from exc
    if value <= 0 or value > 2_147_483_647:
        raise ToolValidationError("order_id is outside the allowed range")
    return value


def _load_mock() -> dict[str, Any]:
    return json.loads(MOCK_FILE.read_text(encoding="utf-8"))


def _function_get(route: str, params: dict[str, Any]) -> dict[str, Any]:
    base = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071/api").rstrip("/")
    key = os.getenv("FUNCTION_KEY", "").strip()
    timeout = int(os.getenv("FUNCTION_TIMEOUT_SECONDS", "20"))
    headers = {"Accept": "application/json"}
    if key:
        headers["x-functions-key"] = key
    response = requests.get(f"{base}/{route}", params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _backend() -> str:
    value = os.getenv("TOOL_BACKEND", "mock").strip().lower()
    if value not in {"mock", "function"}:
        raise ToolValidationError("TOOL_BACKEND must be 'mock' or 'function'")
    return value


def get_revenue_by_region(start_date: str, end_date: str) -> dict[str, Any]:
    """Return revenue grouped by region for an inclusive date range."""
    start = _parse_iso_date(start_date, "start_date")
    end = _parse_iso_date(end_date, "end_date")
    if start > end:
        raise ToolValidationError("start_date must be on or before end_date")
    if (end - start).days > 366:
        raise ToolValidationError("date range cannot exceed 366 days in this POC")

    if _backend() == "function":
        return _function_get("revenue-by-region", {"start_date": start.isoformat(), "end_date": end.isoformat()})

    rows: dict[str, float] = defaultdict(float)
    for order in _load_mock()["orders"]:
        od = date.fromisoformat(order["order_date"])
        if start <= od <= end:
            rows[order["region"]] += float(order["revenue"])
    return {
        "tool": "get_revenue_by_region",
        "source": "mock:dbo.Orders",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "rows": [{"region": region, "revenue": round(value, 2)} for region, value in sorted(rows.items())],
    }


def get_delayed_shipments(report_date: str) -> dict[str, Any]:
    """Return delayed shipments for one date."""
    d = _parse_iso_date(report_date, "report_date")
    if _backend() == "function":
        return _function_get("delayed-shipments", {"date": d.isoformat()})

    rows = [
        order for order in _load_mock()["orders"]
        if order["order_date"] == d.isoformat() and order["shipment_status"] == "Delayed"
    ]
    return {
        "tool": "get_delayed_shipments",
        "source": "mock:dbo.Orders",
        "report_date": d.isoformat(),
        "count": len(rows),
        "rows": rows,
    }


def get_order_summary(order_id: int) -> dict[str, Any]:
    """Return one approved read-only order summary."""
    oid = _validate_order_id(order_id)
    if _backend() == "function":
        return _function_get("order-summary", {"order_id": oid})

    row = next((o for o in _load_mock()["orders"] if int(o["order_id"]) == oid), None)
    return {
        "tool": "get_order_summary",
        "source": "mock:dbo.Orders",
        "order": row,
        "found": row is not None,
    }


def get_metric_source(metric_name: str) -> dict[str, Any]:
    """Return the governed source definition for a supported metric."""
    allowed = {"revenue", "delayed_shipments"}
    normalized = (metric_name or "").strip().lower()
    if normalized not in allowed:
        raise ToolValidationError(f"metric_name must be one of: {', '.join(sorted(allowed))}")
    if _backend() == "function":
        return _function_get("metric-source", {"metric_name": normalized})

    source = _load_mock()["metric_sources"][normalized]
    return {"tool": "get_metric_source", "metric_name": normalized, "source_description": source}


TOOL_DISPATCH = {
    "get_revenue_by_region": get_revenue_by_region,
    "get_delayed_shipments": get_delayed_shipments,
    "get_order_summary": get_order_summary,
    "get_metric_source": get_metric_source,
}
