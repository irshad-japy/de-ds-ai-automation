from rag.chunking import chunk_document
from rag.documents import SourceDocument


def test_chunking_produces_chunks():
    doc = SourceDocument(
        title="Demo",
        source="demo.md",
        category="test",
        content=" ".join([f"word{i}" for i in range(100)]),
        metadata={},
    )
    chunks = chunk_document(doc, chunk_size=30, overlap=5)
    assert len(chunks) >= 2
    assert chunks[0].source == "demo.md"
    assert chunks[0].chunk_id.startswith("demo-")


def test_overlap_must_be_smaller_than_chunk():
    doc = SourceDocument("Demo", "demo.md", "test", "hello world", {})
    try:
        chunk_document(doc, chunk_size=10, overlap=10)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
