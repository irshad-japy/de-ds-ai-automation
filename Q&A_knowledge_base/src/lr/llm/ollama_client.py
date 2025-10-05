import httpx
from .base import Embeddings, Chat
from ..config import settings

_client = httpx.Client(base_url=settings.ollama_base.rstrip("/"), timeout=600)

class OllamaEmbeddings(Embeddings):
    def embed(self, texts):
        # Accept str or list[str]
        if isinstance(texts, str):
            texts = [texts]

        vectors: list[list[float]] = []
        for t in texts:
            r = _client.post("/api/embeddings", json={
                "model": settings.ollama_embed_model,
                "prompt": t
            })

            r.raise_for_status()
            js = r.json()
            # Ollama: {"embedding":[...]}
            if "embedding" in js:
                vectors.append(js["embedding"])
            # Some proxies/alt servers: {"data":[{"embedding":[...]}]}
            elif "data" in js and isinstance(js["data"], list) and js["data"]:
                vectors.append(js["data"][0]["embedding"])
            else:
                raise RuntimeError(
                    f"Unexpected embeddings response from Ollama: {js}"
                )
        return vectors
    
class OllamaChat(Chat):
    def chat(self, messages):
        r = _client.post("/api/chat", json={
            "model": settings.ollama_chat_model,
            "messages": messages,
            "stream": False
        })
        r.raise_for_status()
        return r.json()["message"]["content"]
