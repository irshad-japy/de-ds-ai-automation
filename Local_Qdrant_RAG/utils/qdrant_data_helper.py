# utils/qdrant_data_helper.py

from pathlib import Path
import os, time, requests
from typing import List, Dict, Any

from llama_index.core import Settings, StorageContext, VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

from utils.format import format_context
from utils.schemas import Query, Response

import qdrant_client
# from llama_index.llms.ollama import Ollama   # if you want an LLM

def _is_true(val) -> bool:
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}

class DataIngestor:
    def __init__(self, q_client_url: str, q_api_key: str | None, data_path: str,
                 collection_name: str, embedder_name: str = "sentence-transformers/all-mpnet-base-v2",
                 chunk_size: int = 200):
        self.client = qdrant_client.QdrantClient(url=q_client_url, api_key=q_api_key, timeout=60.0)
        self.data_path = data_path
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.embedder = HuggingFaceEmbedding(model_name=embedder_name)

        # Optional LLM (can omit for ingestion)
        # self.llm = Ollama(model="llama3.2:3b-instruct", base_url="http://localhost:11434", request_timeout=300)

    def ingest(self):
        # Configure modules
        Settings.embed_model = self.embedder
        Settings.chunk_size = self.chunk_size

        data_dir = Path(self.data_path)
        if not data_dir.exists():
            raise FileNotFoundError(f"Data path not found: {data_dir.resolve()}")
        documents = SimpleDirectoryReader(input_dir=str(data_dir)).load_data()

        vs = QdrantVectorStore(client=self.client, collection_name=self.collection_name)
        storage = StorageContext.from_defaults(vector_store=vs)

        # Create the collection with vectors by indexing documents
        index = VectorStoreIndex.from_documents(documents, storage_context=storage)
        return index

class RAG:
    def __init__(self, q_client_url: str, q_api_key: str | None,
                 ollama_base_url: str = "http://localhost:11434",
                 ollama_model: str = "llama3.1:latest",
                 embedder_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self.client = qdrant_client.QdrantClient(url=q_client_url, api_key=q_api_key, timeout=60.0)
        self.llm = Ollama(model=ollama_model, base_url=ollama_base_url, temperature=0, request_timeout=300)
        self.embedder = HuggingFaceEmbedding(model_name=embedder_name)
        self.use_web_fallback = _is_true(os.getenv("WEB_FALLBACK", "no"))
        self._tavily_key = os.getenv("TAVILY_API_KEY")

    def qdrant_index(self, collection_name: str, chunk_size: int = 1024):
        Settings.llm = self.llm
        Settings.embed_model = self.embedder
        Settings.chunk_size = chunk_size

        vs = QdrantVectorStore(client=self.client, collection_name=collection_name)
        storage = StorageContext.from_defaults(vector_store=vs)
        return VectorStoreIndex.from_vector_store(vector_store=vs, storage_context=storage)

    def _web_fallback(self, question: str) -> str:
        """
        Minimal fallback using Tavily (set TAVILY_API_KEY env). If not set, return a short notice.
        """
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "No KB match and no web key configured; set TAVILY_API_KEY to enable web fallback."

        try:
            r = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": api_key, "query": question, "max_results": 3},
                timeout=25,
            )
            r.raise_for_status()
            hits = r.json().get("results", [])[:3]
            snippets = []
            for h in hits:
                # title + content (trim)
                txt = f"{h.get('title','')}\n{(h.get('content') or '')[:1000]}"
                snippets.append(txt)
            ctx = format_context(snippets, max_chars=6000)
            prompt = f"Use the following web snippets to answer.\n\n{ctx}\n\nQ: {question}\nA:"
            out = self.llm.complete(prompt)
            return getattr(out, "text", str(out))
        except Exception as e:
            return f"Web fallback failed: {e}"

    def get_response(self, index, query: Query, append_query: str = "", response_mode: str = "compact",
                     score_threshold: float = 0.35, use_web_fallback: bool | None = None) -> Response:
        qe = index.as_query_engine(response_mode=response_mode)
        res = qe.query(query.query + append_query)

        # Read nodes + scores if present
        nodes = getattr(res, "source_nodes", []) or []
        src: List[Dict[str, Any]] = []
        best = 0.0
        for n in nodes:
            score = float(getattr(n, "score", 0.0) or 0.0)
            best = max(best, score)
            src.append({
                "id": getattr(getattr(n, "node", None), "id_", None),
                "score": score,
                "metadata": getattr(getattr(n, "node", None), "metadata", {}) if getattr(n, "node", None) else {},
            })

        # If KB looks weak, try web
        effective_fallback = self.use_web_fallback if use_web_fallback is None else use_web_fallback
        tavily_enabled = bool(self._tavily_key)
        import pdb; pdb.set_trace()

        if (best < score_threshold or not src):
            if effective_fallback and tavily_enabled:
                answer = self._web_fallback(query.query)
                return Response(search_result=answer, source=src)
            # fallback disabled or no key → return KB result (even if weak)
            text = (getattr(res, "response", None)
                    or getattr(res, "text", None)
                    or "No strong KB match and web fallback disabled.")
            return Response(search_result=text, source=src)

        # KB answer
        text = getattr(res, "response", None) or getattr(res, "text", None) or str(res)
        return Response(search_result=text, source=src)