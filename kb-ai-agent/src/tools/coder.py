from ..util.llm import get_llm

TEMPLATE = """You are a cautious software agent.
Given the Jira spec below and retrieved context, propose a minimal, reversible change.
Return JSON with keys:
- plan: short bullet list
- files: array of {path, content}
SPEC:
{spec}

CONTEXT (KB snippets):
{context}
"""

def propose_code_change(spec: str, kb_snippets: list):
    ctx = "\n\n---\n\n".join([s for s, _m in kb_snippets][:4])
    llm = get_llm()
    prompt = TEMPLATE.format(spec=spec, context=ctx)
    resp = llm.invoke(prompt)
    # basic JSON-guard: model often returns code fences; strip if present
    import json, re
    txt = resp.content
    txt = re.sub(r"^```(json)?|```$", "", txt.strip(), flags=re.MULTILINE)
    plan_files = json.loads(txt)
    return plan_files  # {"plan": "...", "files":[{"path":"a.py","content":"..."}]}
