from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from mssql_python import connect


def _date_or_none(value):
    if not value:
        return None
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _decimal_or_none(value):
    return Decimal(str(value)) if value is not None else None


def invoice_exists(connection_string: str, source_hash: str) -> bool:
    with connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(1) FROM dbo.invoice_header WHERE source_hash = ?", (source_hash,))
        row = cur.fetchone()
        return bool(row and row[0])


def upsert_invoice(connection_string: str, invoice: dict, source_blob: str, source_hash: str) -> None:
    """Idempotent load: MERGE header by source_hash, then replace its lines."""
    with connect(connection_string) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            MERGE dbo.invoice_header AS target
            USING (SELECT ? AS source_hash) AS src
              ON target.source_hash = src.source_hash
            WHEN MATCHED THEN
              UPDATE SET invoice_number=?, invoice_date=?, supplier_name=?, customer_name=?,
                         currency=?, subtotal=?, tax=?, total=?, source_blob=?,
                         document_confidence=?, processed_at=SYSUTCDATETIME()
            WHEN NOT MATCHED THEN
              INSERT (source_hash, invoice_number, invoice_date, supplier_name, customer_name,
                      currency, subtotal, tax, total, source_blob, document_confidence)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                source_hash,
                invoice.get("invoice_number"),
                _date_or_none(invoice.get("invoice_date")),
                invoice.get("supplier_name"),
                invoice.get("customer_name"),
                invoice.get("currency"),
                _decimal_or_none(invoice.get("subtotal")),
                _decimal_or_none(invoice.get("tax")),
                _decimal_or_none(invoice.get("total")),
                source_blob,
                invoice.get("model", {}).get("document_confidence"),
                source_hash,
                invoice.get("invoice_number"),
                _date_or_none(invoice.get("invoice_date")),
                invoice.get("supplier_name"),
                invoice.get("customer_name"),
                invoice.get("currency"),
                _decimal_or_none(invoice.get("subtotal")),
                _decimal_or_none(invoice.get("tax")),
                _decimal_or_none(invoice.get("total")),
                source_blob,
                invoice.get("model", {}).get("document_confidence"),
            ),
        )

        cur.execute("SELECT invoice_key FROM dbo.invoice_header WHERE source_hash = ?", (source_hash,))
        invoice_key = cur.fetchone()[0]
        cur.execute("DELETE FROM dbo.invoice_line WHERE invoice_key = ?", (invoice_key,))

        for item in invoice.get("line_items", []):
            cur.execute(
                """
                INSERT INTO dbo.invoice_line
                    (invoice_key, line_number, description, quantity, unit_price, amount)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_key,
                    item.get("line_number"),
                    item.get("description"),
                    _decimal_or_none(item.get("quantity")),
                    _decimal_or_none(item.get("unit_price")),
                    _decimal_or_none(item.get("amount")),
                ),
            )

        conn.commit()
