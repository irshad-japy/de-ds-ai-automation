from __future__ import annotations

import json
from pathlib import Path


def read_gold_metrics() -> dict:
    path = Path("output/gold/gold_summary.json")
    if not path.exists():
        raise FileNotFoundError("Run the local/Databricks Gold pipeline first")
    return json.loads(path.read_text(encoding="utf-8"))


def supported_metric_answer(question: str) -> str:
    metrics = read_gold_metrics()
    q = question.lower()
    if "revenue" in q:
        return f"total_revenue={metrics['total_revenue']} source={metrics['source']}"
    if "average" in q or "aov" in q:
        return f"average_order_value={metrics['average_order_value']} source={metrics['source']}"
    if "order" in q:
        return f"total_orders={metrics['total_orders']} source={metrics['source']}"
    return f"available_metrics=total_orders,total_revenue,average_order_value source={metrics['source']}"
