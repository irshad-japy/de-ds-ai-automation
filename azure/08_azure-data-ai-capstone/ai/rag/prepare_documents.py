from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    docs = json.loads(Path("data/synthetic/policies.json").read_text(encoding="utf-8"))
    summary_path = Path("output/gold/gold_summary.json")
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        docs.append(
            {
                "id": "METRIC-GOLD-001",
                "title": "Current Gold Order Metrics",
                "category": "metric",
                "source": "output/gold/gold_summary.json",
                "content": (
                    f"The curated Gold dataset contains {summary['total_orders']} orders, "
                    f"total revenue {summary['total_revenue']}, and average order value "
                    f"{summary['average_order_value']}. Generated at {summary['generated_at']}."
                ),
            }
        )
    out = Path("output/search")
    out.mkdir(parents=True, exist_ok=True)
    target = out / "documents.json"
    target.write_text(json.dumps(docs, indent=2), encoding="utf-8")
    print(f"[SUCCESS] Prepared {len(docs)} search documents -> {target}")


if __name__ == "__main__":
    main()
