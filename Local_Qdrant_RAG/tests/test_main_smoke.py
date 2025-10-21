import importlib

def test_main_imports():
    m = importlib.import_module("main")
    assert hasattr(m, "__name__")
