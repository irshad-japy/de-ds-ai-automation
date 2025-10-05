from ..config import settings
from ..llm.ollama_client import OllamaEmbeddings
from ..llm.openrouter_client import OpenRouterEmbeddings

def get_embedder():
    if settings.provider == "openrouter":
        return OpenRouterEmbeddings()
    return OllamaEmbeddings()
