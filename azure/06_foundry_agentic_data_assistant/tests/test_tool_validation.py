import os
import pytest

os.environ["TOOL_BACKEND"] = "mock"

from agent.tools import ToolValidationError, get_metric_source, get_order_summary, get_revenue_by_region


def test_revenue_happy_path():
    result = get_revenue_by_region("2026-09-01", "2026-09-02")
    assert result["rows"]
    assert result["tool"] == "get_revenue_by_region"


def test_revenue_rejects_reversed_dates():
    with pytest.raises(ToolValidationError):
        get_revenue_by_region("2026-09-03", "2026-09-01")


def test_order_id_validation():
    with pytest.raises(ToolValidationError):
        get_order_summary(-1)


def test_metric_allowlist():
    with pytest.raises(ToolValidationError):
        get_metric_source("drop_table")
