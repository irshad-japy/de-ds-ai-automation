import importlib

tx = importlib.import_module("utils.text_transformatuons")

def test_module_loads():
    assert hasattr(tx, "__name__")

def test_normalize_like_helpers_exist():
    names = dir(tx)
    has_any = any(k in names for k in ["normalize_text", "normalize_whitespace", "clean_text"])
    assert has_any, "Expected a text normalization helper in text_transformatuons.py"
