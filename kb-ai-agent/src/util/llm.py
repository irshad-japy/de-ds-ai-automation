import os
from langchain_openai import ChatOpenAI

def get_llm(model: str = "gpt-4o-mini", temperature: float = 0.2):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing.")
    return ChatOpenAI(api_key=api_key, model=model, temperature=temperature)
