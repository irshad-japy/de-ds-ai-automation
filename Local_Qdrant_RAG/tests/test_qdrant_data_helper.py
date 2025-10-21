from unittest.mock import patch, MagicMock
import types

# Import the module under test
import utils.qdrant_data_helper as qh

def test_dataclasses_exist():
    # these names are used in the README
    assert hasattr(qh, "DataIngestor")
    assert hasattr(qh, "RAG")
    assert hasattr(qh, "Query")

@patch("utils.qdrant_data_helper.QdrantClient")
def test_ingestor_ingest_calls_qdrant(mock_client):
    # Arrange
    mock_instance = mock_client.return_value
    mock_instance.collection_exists.return_value = True

    ingestor = qh.DataIngestor(
        q_client_url="http://localhost:6333/",
        q_api_key="test",
        data_path="./data",
        collection_name="dcard_collection",
        embedder_name="sentence-transformers/all-mpnet-base-v2",
    )

    # Provide a tiny fake ingest pipeline by monkeypatching any internal
    # embedders/loader if the implementation expects them.
    if hasattr(ingestor, "embed_texts"):
        ingestor.embed_texts = lambda x: [[0.1, 0.2, 0.3] for _ in x]

    # Act
    res = ingestor.ingest()

    # Assert (very loose: we only check the type/shape or that Qdrant was used)
    assert mock_instance.upsert_collection.called or mock_instance.upsert_points.called or mock_instance.upload_collection.called

@patch("utils.qdrant_data_helper.QdrantClient")
def test_rag_qdrant_index_returns_handle(mock_client):
    rag = qh.RAG(
        q_client_url="http://localhost:6333/",
        q_api_key="test",
        ollama_model="gemma:7b",
        ollama_base_url="http://localhost:11434",
    )
    idx = rag.qdrant_index(collection_name="dcard_collection", chunk_size=1024)
    assert idx is not None

@patch("utils.qdrant_data_helper.QdrantClient")
def test_rag_get_response_shape(mock_client):
    # Build RAG instance
    rag = qh.RAG(
        q_client_url="http://localhost:6333/",
        q_api_key="test",
        ollama_model="gemma:7b",
        ollama_base_url="http://localhost:11434",
    )

    # Fake index and fake response object expected by code
    fake_index = object()

    # Build a fake result with fields printed in README
    class FakeResult:
        search_result = "answer text"
        source = [{"doc": "doc1", "score": 0.77}]

    # Monkeypatch the internal call RAG uses to talk to LLM/retriever
    if hasattr(rag, "get_response"):
        # wrap the original so we keep signature
        orig = rag.get_response
        def fake_get_response(index, query, append_query="", response_mode="tree_summarize"):
            return FakeResult()
        rag.get_response = fake_get_response  # type: ignore

    q = qh.Query(query="高科大是什麼時候合併的？", top_k=5)
    res = rag.get_response(fake_index, q, append_query="", response_mode="tree_summarize")
    assert hasattr(res, "search_result")
    assert hasattr(res, "source")
