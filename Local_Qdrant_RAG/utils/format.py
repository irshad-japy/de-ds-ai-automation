from typing import Iterable, Dict, Any, Optional

def format_context(chunks: Iterable[str], max_chars: int = 6000) -> str:
    joined = "\n\n".join((c or "").strip() for c in chunks if c)
    return joined[:max_chars].rstrip()

def format_prompt(question: str, context: str, system: Optional[str] = None) -> str:
    sys = f"System: {system.strip()}\n\n" if system else ""
    return f"{sys}Context:\n{context}\n\nUser Question:\n{question}\n\nAnswer:"

def format_sources(sources: Iterable[Dict[str, Any]], max_sources: int = 5) -> str:
    rows = []
    for i, s in enumerate(sources):
        if i >= max_sources:
            break
        sid = s.get("id") or s.get("doc_id") or f"s{i+1}"
        score = s.get("score")
        title = (s.get("metadata") or {}).get("title") or (s.get("metadata") or {}).get("file") or "Untitled"
        rows.append(f"- [{sid}] {title} (score={score})")
    return "Sources:\n" + ("\n".join(rows) if rows else "(none)")
