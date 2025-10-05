from openai import OpenAI
from .base import Embeddings, Chat
from ..config import settings

client = OpenAI(base_url=settings.openrouter_base, api_key=settings.openrouter_api_key)

class OpenRouterEmbeddings(Embeddings):
    def embed(self, texts):
        resp = client.embeddings.create(model=settings.openrouter_embed_model, input=texts)
        return [d.embedding for d in resp.data]

class OpenRouterChat(Chat):
    def chat(self, messages):
        # messages: [{"role": "system"/"user"/"assistant", "content": "..."}]
        resp = client.chat.completions.create(model=settings.openrouter_chat_model, messages=messages)
        return resp.choices[0].message.content
