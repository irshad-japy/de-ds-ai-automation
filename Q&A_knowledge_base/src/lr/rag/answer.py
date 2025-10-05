from ..config import settings
from ..llm.ollama_client import OllamaChat
from ..llm.openrouter_client import OpenRouterChat
from .retrieve import retrieve

def get_chat():
    if settings.provider == "openrouter":
        return OpenRouterChat()
    return OllamaChat()

SYSTEM_PROMPT = (
    "Role: Local-first RAG Copilot.\n"
    "Answer using only the retrieved context.\n"
    "Rules:\n"
    "• Be concise: ≤7 bullets; exact figures/dates\n"
    "• Cite short snippets as [#]\n"
    "• If context is insufficient: reply exactly “I don’t know” and suggest one next step\n"
    "• When data is tabular, summarize key rows/cols before concluding\n"
    "• Distinguish KNOW (from context) vs INFER (logic)\n"
    "• Never browse the web or invent sources\n"
)

def answer(query: str, only_ext: str | None = None):
    # stricter retrieval — favor PDFs if you're asking about PDFs
    hits = retrieve(query, k=6, only_ext=only_ext, min_score=0.25)

    if not hits:
        return {
            "answer": "I don’t know",
            "bullets": [],
            "next_step": "ingest more files into ./input (especially relevant PDFs/CSVs).",
            "used_chunks": [],
        }

    # Build a compact context with [#] tags
    blocks = []
    used = []
    for idx, (pid, score, pl) in enumerate(hits, start=1):
        src = f"{pl.get('source','?')}::{pl.get('chunk',0)}"
        snippet = pl.get("text","").strip().replace("\n", " ")[:900]
        blocks.append(f"[{idx}] {snippet}")
        used.append({"source": pl.get("source"), "chunk": pl.get("chunk"), "score": round(score, 4)})

    context = "\n\n".join(blocks)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {query}\n\nContext:\n{context}"},
    ]

    chat = OllamaChat()
    out = chat.chat(messages)

    return {
        "answer": out,
        "used_chunks": used,
    }
