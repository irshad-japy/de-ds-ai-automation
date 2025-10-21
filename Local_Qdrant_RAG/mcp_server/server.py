# mcp_server/server.py
"""
MCP server that exposes your Local_Qdrant_RAG "ingest" and "ask" as tools.
- Uses FastMCP from the official MCP Python SDK.
- Wraps your existing Qdrant + LlamaIndex + Ollama setup.
Run (dev):    mcp dev mcp_server/server.py
Install to Claude Desktop: mcp install mcp_server/server.py --name "Local Qdrant RAG"
"""

from __future__ import annotations

import os
from typing import Any, TypedDict, Optional

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

# Reuse your project code
from utils.schemas import Query
from utils.qdrant_data_helper import RAG

# Optional: direct ingestion via LlamaIndex (does not rely on utils.DataIngestor)
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from qdrant_client import QdrantClient

DEFAULT_COLLECTION = os.getenv("COLLECTION_NAME", "dcard_collection")
DEFAULT_EMBEDDER = os.getenv("EMBEDDER_NAME", "sentence-transformers/all-mpnet-base-v2")

mcp = FastMCP("Local_Qdrant_RAG_MCP")

def _make_rag() -> RAG:
    host = os.getenv("RAG_HOST", "localhost")
    return RAG(
        q_client_url=os.getenv("QDRANT_URL", f"http://{host}:6333"),
        q_api_key=os.getenv("QDRANT_API_KEY") or None,
        ollama_base_url=os.getenv("OLLAMA_BASE", f"http://{host}:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
        embedder_name=DEFAULT_EMBEDDER,
    )

@mcp.tool()
def ingest_folder(
    folder: str,
    collection: str = DEFAULT_COLLECTION,
    chunk_size: int = 1024,
) -> dict[str, object]:
    """Ingest all files from 'folder' into the specified Qdrant collection.
    Returns a small JSON result with document & node counts.
    """
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"folder not found: {os.path.abspath(folder)}")

    # Connect to Qdrant
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY") or None,
        timeout=60,
    )

    # Prepare vector store + storage context
    vs = QdrantVectorStore(client=client, collection_name=collection)
    storage = StorageContext.from_defaults(vector_store=vs)

    # Embed with HF model locally (keeps your stack local-first)
    embedder = HuggingFaceEmbedding(model_name=DEFAULT_EMBEDDER, max_length=512)

    # Load and index
    docs = SimpleDirectoryReader(folder).load_data()
    index = VectorStoreIndex.from_documents(docs, storage_context=storage, embed_model=embedder)
    # Ensure the index is materialized (VectorStoreIndex constructor already inserts vectors)
    return {"ok": True, "collection": collection, "docs_indexed": len(docs)}

class AskResult(TypedDict):
    answer: str
    sources: list[dict[str, object]]

@mcp.tool()
def ask(
    query: str,
    top_k: int = 5,
    collection: str = DEFAULT_COLLECTION,
    response_mode: str = "compact",
    web_fallback: bool = False,
) -> AskResult:
    """Ask a question against your KB (Qdrant) and optionally use web fallback.
    Returns the final answer plus a structured list of sources.
    """
    rag = _make_rag()
    # Reuse your project's index builder
    index = rag.qdrant_index(collection_name=collection, chunk_size=1024)

    q = Query(query=query, similarity_top_k=top_k)

    # Be robust to signature differences in your current RAG class
    try:
        res = rag.get_response(index=index, query=q, response_mode=response_mode, use_web_fallback=web_fallback)
    except TypeError:
        # older signature support
        res = rag.get_response(index=index, query=q, append_query="", response_mode=response_mode)

    # Normalize output
    answer = getattr(res, "search_result", None) or getattr(res, "text", None) or str(res)
    sources = getattr(res, "source", [])
    return {"answer": answer, "sources": sources}

@mcp.resource("kb://collections/{name}")
def collection_info(name: str) -> str:
    """Return basic Qdrant collection info as a string (for quick inspection)."""
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY") or None,
        timeout=30,
    )
    info = client.get_collection(name)
    return str(info)

@mcp.prompt()
def kb_answer_prompt(question: str) -> str:
    """Reusable prompt template the client can load and fill.
    Clients can combine this with tool calls for best results.
    """
    return f"Answer this question using knowledge base + citations:\n\nQ: {question}\nA:"

if __name__ == "__main__":
    # Default to stdio transport so Claude Desktop / Cursor can use it.
    mcp.run()
