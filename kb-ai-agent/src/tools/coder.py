"""
python -m src.tools.coder
"""

# src/tools/coder.py
from __future__ import annotations

from typing import Dict, Any, List, Tuple

# kb_snippets: List[Tuple[doc:str, meta:dict]]
def propose_code_change(spec: str, kb_snippets: List[Tuple[str, dict]]) -> Dict[str, Any]:
    """
    Return a plan dict:
      { "plan": "...", "branch": "auto/KEY-123-...", "files": [{"path":"...","content":"..."}] }
    If no LLM configured, fallback to adding docs/jira/<KEY>.md from the spec.
    """
    # Try to infer issue key from KB meta sources (jira://KEY)
    key = None
    for _, meta in kb_snippets:
        src = (meta or {}).get("source", "")
        if src.startswith("jira://"):
            key = src.split("jira://", 1)[1].split("/", 1)[0].split("#", 1)[0]
            break
    if not key:
        key = "TASK"

    # You can wire your LLM here. For now: simple deterministic plan.
    branch = f"auto/{key}"
    plan_text = (
        f"Create a documentation stub for {key} so reviewers can discuss scope.\n"
        f"Further code edits can be added in a follow-up commit."
    )
    file_path = f"docs/jira/{key}-plan.md"
    body = [
        f"# Plan for {key}",
        "",
        "## Spec",
        spec or "N/A",
        "",
        "## Retrieved Context",
        *[f"- { (m or {}).get('source','?') }" for _, m in kb_snippets[:5]],
        "",
        "## Proposed Next Steps",
        "1. Confirm acceptance criteria with stakeholders.",
        "2. Implement the smallest vertical slice.",
        "3. Add tests and docs.",
    ]
    return {
        "plan": plan_text,
        "branch": branch,
        "files": [{"path": file_path, "content": "\n".join(body)}],
    }

