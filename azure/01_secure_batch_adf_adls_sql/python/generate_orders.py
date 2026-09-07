#!/usr/bin/env python3
"""
python azure/poc_01_secure_batch_adf_adls_sql/python/generate_orders.py --output azure/poc_01_secure_batch_adf_adls_sql/data/generated/orders_002.csv --rows 500

"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATUSES = ["NEW", "PAID", "SHIPPED", "CANCELLED"]


def build_rows(row_count: int, seed: int) -> list[dict[str, object]]:
    if row_count < 3:
        raise ValueError("--rows must be at least 3 so two bad rows and one valid row can be produced")

    rng = random.Random(seed)
    base = datetime(2026, 8, 28, 3, 0, tzinfo=timezone.utc)
    rows: list[dict[str, object]] = []

    for i in range(1, row_count + 1):
        qty = rng.randint(1, 5)
        price = round(rng.uniform(50, 2500), 2)
        rows.append(
            {
                "order_id": 100000 + i,
                "customer_id": 5000 + rng.randint(1, 40),
                "order_ts": (base + timedelta(minutes=i * 7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "product_id": 9000 + rng.randint(1, 25),
                "quantity": qty,
                "unit_price": f"{price:.2f}",
                "status": rng.choice(STATUSES),
            }
        )

    # Bad row 1: valid SQL type, invalid business rule.
    rows[-2]["quantity"] = -2

    # Bad row 2: incompatible with DECIMAL(12,2) at the SQL sink.
    rows[-1]["unit_price"] = "NOT_A_PRICE"

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic order data for Azure POC-01")
    parser.add_argument("--rows", type=int, default=30, help="Total rows to create (default: 30)")
    parser.add_argument("--seed", type=int, default=26, help="Random seed for repeatability")
    parser.add_argument(
        "--output",
        default="data/generated/orders_001.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    rows = build_rows(args.rows, args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "order_id",
        "customer_id",
        "order_ts",
        "product_id",
        "quantity",
        "unit_price",
        "status",
    ]

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows: {output.resolve()}")
    print(f"Expected valid curated rows after POC validation: {len(rows) - 2}")
    print("Bad row #1: quantity = -2")
    print("Bad row #2: unit_price = NOT_A_PRICE")


if __name__ == "__main__":
    main()
