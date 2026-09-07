import json
import os

os.environ["TOOL_BACKEND"] = "mock"

from agent.tools import get_delayed_shipments, get_metric_source, get_order_summary, get_revenue_by_region


def show(name, value):
    print("=" * 80)
    print(name)
    print(json.dumps(value, indent=2, default=str))


def main():
    show("Revenue", get_revenue_by_region("2026-09-01", "2026-09-02"))
    show("Delayed", get_delayed_shipments("2026-09-02"))
    show("Order", get_order_summary(1001))
    show("Metric source", get_metric_source("revenue"))
    print("\n[SUCCESS] All local safe tools executed.")


if __name__ == "__main__":
    main()
