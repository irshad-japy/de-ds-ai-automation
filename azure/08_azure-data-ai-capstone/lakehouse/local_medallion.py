from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def run_pipeline(input_csv: Path, output_root: Path) -> dict:
    bronze_dir = output_root / "bronze"
    silver_dir = output_root / "silver"
    gold_dir = output_root / "gold"
    for d in (bronze_dir, silver_dir, gold_dir):
        d.mkdir(parents=True, exist_ok=True)

    bronze = pd.read_csv(input_csv)
    bronze["ingestion_ts"] = datetime.now(timezone.utc).isoformat()
    bronze.to_csv(bronze_dir / "orders.csv", index=False)

    silver = bronze.copy()
    silver["order_date"] = pd.to_datetime(silver["order_date"], errors="coerce")
    silver["quantity"] = pd.to_numeric(silver["quantity"], errors="coerce")
    silver["unit_price"] = pd.to_numeric(silver["unit_price"], errors="coerce")
    silver = silver.dropna(subset=["order_id", "order_date", "quantity", "unit_price"])
    silver = silver[(silver["quantity"] > 0) & (silver["unit_price"] >= 0)]
    silver = silver.drop_duplicates(subset=["order_id"], keep="last")
    silver["line_amount"] = silver["quantity"] * silver["unit_price"]
    silver.to_csv(silver_dir / "orders_clean.csv", index=False)

    customer = (
        silver.groupby("customer_id", as_index=False)
        .agg(total_orders=("order_id", "nunique"), total_units=("quantity", "sum"), total_revenue=("line_amount", "sum"))
        .sort_values("total_revenue", ascending=False)
    )
    customer.to_csv(gold_dir / "customer_metrics.csv", index=False)

    total_orders = int(silver["order_id"].nunique())
    total_revenue = float(silver["line_amount"].sum())
    summary = {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(total_revenue / total_orders, 2) if total_orders else 0.0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "output/gold/gold_summary.json",
    }
    (gold_dir / "gold_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
