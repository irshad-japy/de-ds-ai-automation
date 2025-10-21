import os
import pytest

@pytest.fixture(autouse=True)
def set_env():
    os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
    os.environ.setdefault("QDRANT_API_KEY", "test")
    os.environ.setdefault("OLLAMA_BASE", "http://localhost:11434")
    os.environ.setdefault("OLLAMA_MODEL", "gemma:7b")
    os.environ.setdefault("COLLECTION_NAME", "dcard_collection")
    yield
