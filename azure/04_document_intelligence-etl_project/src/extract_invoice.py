from __future__ import annotations

from io import BytesIO
from typing import Any

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

from .config import Settings

def _get(mapping: Any, key: str, default=None):
    if mapping is None:
        return default
    if isinstance(mapping, dict):
        return mapping.get(key, default)
    try:
        return mapping.get(key, default)
    except Exception:
        return getattr(mapping, key, default)

def _content(field: Any) -> str | None:
    if not field:
        return None
    value = _get(field, "content")
    if value is not None:
        return str(value).strip()
    value = _get(field, "valueString")
    if value is not None:
        return str(value).strip()
    return None

def _confidence(field: Any) -> float | None:
    if not field:
        return None
    value = _get(field, "confidence")
    return float(value) if value is not None else None

def _number(field: Any) -> float | None:
    if not field:
        return None

    for k in ("valueNumber", "valueInteger"):
        value = _get(field, k)
        if value is not None:
            return float(value)

    currency = _get(field, "valueCurrency")
    if currency:
        amount = _get(currency, "amount")
        if amount is not None:
            return float(amount)

    raw = _content(field)
    if not raw:
        return None
    cleaned = raw.replace(",", "")
    for symbol in ("$", "₹", "€", "£", "USD", "INR", "EUR", "GBP"):
        cleaned = cleaned.replace(symbol, "")
    cleaned = cleaned.strip()
    try:
        return float(cleaned)
    except ValueError:
        return None

def _currency_code(*fields: Any) -> str | None:
    for field in fields:
        currency = _get(field, "valueCurrency") if field else None
        if currency:
            code = _get(currency, "currencyCode")
            if code:
                return str(code)
    return None

def _date_text(field: Any) -> str | None:
    if not field:
        return None
    value = _get(field, "valueDate")
    if value is not None:
        return str(value)
    return _content(field)

def _field(fields: dict, name: str):
    return fields.get(name) if fields else None

def build_client(settings: Settings) -> DocumentIntelligenceClient:
    # Beginner/local path: API key loaded from environment (.env, not source code).
    # Azure-hosted path: leave the key empty and use Managed Identity / Entra ID.
    if settings.document_intelligence_api_key:
        credential = AzureKeyCredential(settings.document_intelligence_api_key)
    else:
        credential = DefaultAzureCredential()
    return DocumentIntelligenceClient(
        endpoint=settings.document_intelligence_endpoint,
        credential=credential,
    )

def analyze_invoice_bytes(document_bytes: bytes, settings: Settings) -> tuple[dict, dict]:
    """Return (raw_result_dict, normalized_invoice)."""
    client = build_client(settings)
    with BytesIO(document_bytes) as stream:
        poller = client.begin_analyze_document("prebuilt-invoice", body=stream)
        result = poller.result()

    raw = result.as_dict()
    if not raw.get("documents"):
        raise ValueError("Document Intelligence returned no invoice document.")

    document = raw["documents"][0]
    fields = document.get("fields", {})

    invoice_id = _field(fields, "InvoiceId")
    invoice_date = _field(fields, "InvoiceDate")
    vendor_name = _field(fields, "VendorName")
    customer_name = _field(fields, "CustomerName")
    subtotal = _field(fields, "SubTotal")
    total_tax = _field(fields, "TotalTax")
    invoice_total = _field(fields, "InvoiceTotal")

    line_items: list[dict] = []
    items_field = _field(fields, "Items")
    value_array = _get(items_field, "valueArray", []) or []
    for index, item in enumerate(value_array, start=1):
        obj = _get(item, "valueObject", {}) or {}
        description = _field(obj, "Description")
        quantity = _field(obj, "Quantity")
        unit_price = _field(obj, "UnitPrice")
        amount = _field(obj, "Amount")

        line_items.append(
            {
                "line_number": index,
                "description": _content(description),
                "quantity": _number(quantity),
                "unit_price": _number(unit_price),
                "amount": _number(amount),
                "confidence": {
                    "description": _confidence(description),
                    "quantity": _confidence(quantity),
                    "unit_price": _confidence(unit_price),
                    "amount": _confidence(amount),
                },
            }
        )

    normalized = {
        "invoice_number": _content(invoice_id),
        "invoice_date": _date_text(invoice_date),
        "supplier_name": _content(vendor_name),
        "customer_name": _content(customer_name),
        "currency": _currency_code(invoice_total, subtotal, total_tax),
        "line_items": line_items,
        "subtotal": _number(subtotal),
        "tax": _number(total_tax),
        "total": _number(invoice_total),
        "confidence": {
            "invoice_number": _confidence(invoice_id),
            "invoice_date": _confidence(invoice_date),
            "supplier_name": _confidence(vendor_name),
            "customer_name": _confidence(customer_name),
            "subtotal": _confidence(subtotal),
            "tax": _confidence(total_tax),
            "total": _confidence(invoice_total),
        },
        "model": {
            "model_id": raw.get("modelId") or raw.get("model_id") or "prebuilt-invoice",
            "api_version": raw.get("apiVersion") or raw.get("api_version"),
            "document_confidence": document.get("confidence"),
        },
    }
    return raw, normalized
