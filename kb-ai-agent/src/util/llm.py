import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMConfig:
    provider: str  # "cohere" | "openai" | "ollama"
    llm_model: str
    embed_model: str | None
    cohere_api_key: str | None
    openai_api_key: str | None
    ollama_base_url: str | None

def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() == "true"

def get_llm_config() -> LLMConfig:
    use_cohere = _bool("USE_COHERE")
    use_openai = _bool("USE_OPENAI")
    use_ollama = _bool("USE_OLLAMA")

    # default to Cohere if none chosen
    if not any([use_cohere, use_openai, use_ollama]):
        use_cohere = True

    if use_cohere:
        return LLMConfig(
            provider="cohere",
            llm_model=os.getenv("COHERE_LLM_MODEL", "command-r"),
            embed_model=os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0"),
            cohere_api_key=os.getenv("COHERE_API_KEY"),
            openai_api_key=None,
            ollama_base_url=None
        )
    elif use_openai:
        return LLMConfig(
            provider="openai",
            llm_model=os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini"),
            embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large"),
            cohere_api_key=None,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_base_url=None
        )
    else:
        return LLMConfig(
            provider="ollama",
            llm_model=os.getenv("OLLAMA_LLM_MODEL", "llama3.1"),
            embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            cohere_api_key=None,
            openai_api_key=None,
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )

# ---------- Embeddings (Cohere / OpenAI / Ollama) ----------
from langchain.embeddings.base import Embeddings
from typing import List

class CohereEmbeddings(Embeddings):
    """
    Minimal Cohere embeddings adapter for Chroma:
    Uses cohere.Embeddings API with 'input_type="search_document"' for docs
    and 'search_query' for queries.
    """
    def __init__(self, api_key: str, model: str):
        import cohere
        self.client = cohere.Client(api_key)
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Cohere recommends input_type="search_document" for corpus
        resp = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"
        )
        return resp.embeddings  # type: ignore

    def embed_query(self, text: str) -> List[float]:
        resp = self.client.embed(
            texts=[text],
            model=self.model,
            input_type="search_query"
        )
        return resp.embeddings[0]  # type: ignore

class OllamaEmbeddings(Embeddings):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import requests
        out = []
        for t in texts:
            r = requests.post(f"{self.base_url}/api/embeddings",
                              json={"model": self.model, "prompt": t})
            r.raise_for_status()
            out.append(r.json()["embedding"])
        return out

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

def get_embeddings():
    cfg = get_llm_config()
    if cfg.provider == "cohere":
        if not cfg.cohere_api_key:
            raise RuntimeError("COHERE_API_KEY is missing.")
        return CohereEmbeddings(api_key=cfg.cohere_api_key, model=cfg.embed_model or "embed-english-v3.0")
    
    else:
        return OllamaEmbeddings(base_url=cfg.ollama_base_url, model=cfg.embed_model)

# ---------- Text generation (llm_complete) ----------
def llm_complete(prompt: str, temperature: float = 0.2) -> str:
    cfg = get_llm_config()
    if cfg.provider == "cohere":
        if not cfg.cohere_api_key:
            raise RuntimeError("COHERE_API_KEY is missing.")
        import cohere
        client = cohere.Client(cfg.cohere_api_key)
        # Chat API (supports tools/system messages if you expand later)
        resp = client.chat(
            model=cfg.llm_model,
            message=prompt,
            temperature=temperature,
        )
        # Newer Cohere SDKs expose .text for chat responses
        return (resp.text or "").strip()
    elif cfg.provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=cfg.openai_api_key)
        res = client.chat.completions.create(
            model=cfg.llm_model,
            messages=[
                {"role": "system", "content": "You are a concise helpful coding assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return res.choices[0].message.content.strip()
    else:
        import requests
        r = requests.post(
            f"{cfg.ollama_base_url}/api/chat",
            json={
                "model": cfg.llm_model,
                "messages":[
                    {"role":"system","content":"You are a concise helpful coding assistant."},
                    {"role":"user","content": prompt}
                ],
                "options":{"temperature":temperature}
            }
        )
        r.raise_for_status()
        data = r.json()
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"].strip()
        return data.get("content","").strip()
