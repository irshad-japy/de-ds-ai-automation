#!/usr/bin/env python3
"""

python azure/poc_01_secure_batch_adf_adls_sql/python/inspect_orders.py --file azure/poc_01_secure_batch_adf_adls_sql/data/generated/orders_001.csv
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
ALLOWED_STATUSES = {"NEW", "PAID", "SHIPPED", "CANCELLED"}
EXPECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_ts",
    "product_id",
    "quantity",
    "unit_price",
    "status",
]

def inspect(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(f"Unexpected columns: {reader.fieldnames}; expected: {EXPECTED_COLUMNS}")
        rows = list(reader)

    type_invalid: list[tuple[int, str]] = []
    business_invalid: list[tuple[int, str]] = []
    valid = 0

    for line_no, row in enumerate(rows, start=2):
        try:
            order_id = int(row["order_id"])
            customer_id = int(row["customer_id"])
            product_id = int(row["product_id"])
            quantity = int(row["quantity"])
            price = Decimal(row["unit_price"])
        except (ValueError, InvalidOperation) as exc:
            type_invalid.append((line_no, str(exc)))
            continue

        reasons: list[str] = []
        if order_id <= 0:
            reasons.append("order_id must be > 0")
        if customer_id <= 0:
            reasons.append("customer_id must be > 0")
        if product_id <= 0:
            reasons.append("product_id must be > 0")
        if quantity <= 0:
            reasons.append("quantity must be > 0")
        if price < 0:
            reasons.append("unit_price must be >= 0")
        if row["status"] not in ALLOWED_STATUSES:
            reasons.append("invalid status")

        if reasons:
            business_invalid.append((line_no, "; ".join(reasons)))
        else:
            valid += 1

    print(f"File: {path.resolve()}")
    print(f"Rows: {len(rows)}")
    print(f"Type-invalid rows: {len(type_invalid)}")
    for item in type_invalid:
        print(f"  line {item[0]}: {item[1]}")
    print(f"Business-invalid rows: {len(business_invalid)}")
    for item in business_invalid:
        print(f"  line {item[0]}: {item[1]}")
    print(f"Expected curated rows: {valid}")

    return valid

def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a POC-01 order CSV")
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    inspect(args.csv_file)

if __name__ == "__main__":
    main()
