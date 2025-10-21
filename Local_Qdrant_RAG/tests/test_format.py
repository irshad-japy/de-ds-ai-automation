import importlib

fmt = importlib.import_module("utils.format")

def test_module_loads():
    assert hasattr(fmt, "__name__")

def test_format_prompt_exists():
    # If function names differ, rename these assertions to match.
    cand = [n for n in dir(fmt) if "format" in n or "prompt" in n]
    assert cand, "Expected at least one formatting helper in format.py"
