from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

# azure_functions/shared -> azure_functions -> project root
PROJECT_DATA = Path(__file__).resolve().parents[2] / "data" / "mock_business_data.json"
FUNCTION_DATA = Path(__file__).resolve().parents[1] / "mock_business_data.json"
DATA_FILE = PROJECT_DATA if PROJECT_DATA.exists() else FUNCTION_DATA


class MockRepository:
    def __init__(self):
        self.data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    def revenue_by_region(self, start_date: str, end_date: str):
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
        totals = defaultdict(float)
        for row in self.data["orders"]:
            d = date.fromisoformat(row["order_date"])
            if start <= d <= end:
                totals[row["region"]] += float(row["revenue"])
        return [{"region": k, "revenue": round(v, 2)} for k, v in sorted(totals.items())]

    def delayed_shipments(self, report_date: str):
        return [
            row for row in self.data["orders"]
            if row["order_date"] == report_date and row["shipment_status"] == "Delayed"
        ]

    def order_summary(self, order_id: int):
        return next((row for row in self.data["orders"] if int(row["order_id"]) == order_id), None)

    def metric_source(self, metric_name: str):
        return {"metric_name": metric_name, "source_description": self.data["metric_sources"].get(metric_name)}
