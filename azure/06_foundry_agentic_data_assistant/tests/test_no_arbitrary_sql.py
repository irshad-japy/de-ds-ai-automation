from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_agent_tool_layer_has_no_execute_sql():
    text = (ROOT / "agent" / "tools.py").read_text(encoding="utf-8").lower()
    assert "def execute_sql" not in text


def test_sql_repository_has_no_generic_execute_method():
    text = (ROOT / "azure_functions" / "shared" / "sql_repository.py").read_text(encoding="utf-8").lower()
    assert "def execute_sql" not in text
    assert "usp_getrevenuebyregion" in text
    assert "usp_getdelayedshipments" in text
    assert "usp_getordersummary" in text
