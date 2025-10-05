def mk_kb_markdown(payload, tldr, bullets):
    tags = ", ".join(payload.get("tags", []))
    lines = []
    lines.append(f"# {payload.get('title','POC')}")
    lines.append(f"**POC Key:** {payload['poc_key']}")
    lines.append(f"**Goal:** {payload.get('goal','')}")
    lines.append(f"**Context:** {payload.get('context','')}")
    lines.append(f"**TL;DR:** {tldr}")
    lines.append("## Steps")
    for s in payload.get("steps_taken", []):
        lines.append(f"1. {s}")
    lines.append("## Commands\n```bash")
    lines.extend(payload.get("commands", []))
    lines.append("```\n## Issues & Fixes")
    for i,f in zip(payload.get("issues", []), payload.get("fixes", [])):
        lines.append(f"- Issue: {i} → Fix: {f}")
    if payload.get("outcome"):
        lines.append("## Outcome")
        lines.append(payload["outcome"])
    lines.append("## Links")
    for l in payload.get("links", []):
        lines.append(f"- {l}")
    lines.append("## Tags")
    lines.append("`" + tags + "`")
    return "\n".join(lines)
