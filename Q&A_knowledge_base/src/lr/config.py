from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    provider: str = os.getenv("PROVIDER", "ollama").lower()

    # ollama
    ollama_base: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1")
    ollama_embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    # openrouter
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_base: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_chat_model: str = os.getenv("OPENROUTER_CHAT_MODEL", "meta-llama/llama-3.1-70b-instruct")
    openrouter_embed_model: str = os.getenv("OPENROUTER_EMBED_MODEL", "nomic-ai/nomic-embed-text-v1")

    # qdrant
    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "local_rag_chunks")

    # app
    app_env: str = os.getenv("APP_ENV", "dev")
    log_dir: str = os.getenv("LOG_DIR", "./logs")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
