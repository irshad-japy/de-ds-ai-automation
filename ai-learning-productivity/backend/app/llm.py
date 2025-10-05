import os, httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "").rstrip("/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def simple_llm_summarize(payload: dict) -> dict:
    """
    Tries OpenAI → Ollama → rule-based fallback.
    Returns dict parts to be inserted in SummarizeOutput.
    """
    text = "\n".join([
        payload.get("title",""),
        payload.get("goal",""),
        "Steps: " + "; ".join(payload.get("steps_taken", [])),
        "Issues: " + "; ".join(payload.get("issues", [])),
        "Fixes: " + "; ".join(payload.get("fixes", [])),
        "Outcome: " + payload.get("outcome",""),
    ])

    # 1) OpenAI (optional)
    if OPENAI_API_KEY:
        try:
            import json
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={
                        "model": "gpt-4o-mini",  # cheap, change if you like
                        "messages": [
                            {"role":"system","content":"Summarize concisely into TLDR + 5 bullets + 1 paragraph voiceover; return JSON keys: tldr, bullets[], voiceover."},
                            {"role":"user","content": text}
                        ],
                        "temperature": 0.3
                    }
                )
            js = r.json()
            content = js["choices"][0]["message"]["content"]
            # rough parse; if JSON, use it; else fallback
            try:
                data = json.loads(content)
                return {
                    "tldr": data.get("tldr",""),
                    "bullets": data.get("bullets", []),
                    "voiceover": data.get("voiceover","")
                }
            except Exception:
                pass
        except Exception:
            pass

    # 2) Ollama (optional)
    if OLLAMA_URL:
        try:
            prompt = ("Summarize concisely:\n" + text + 
                      "\nReturn TLDR (1 line) + 5 bullets + 1 short voiceover.")
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": "llama3", "prompt": prompt, "stream": False}
                )
            out = r.json().get("response","")
            # Quick heuristic split
            lines = [ln.strip("-• ").strip() for ln in out.splitlines() if ln.strip()]
            tldr = lines[0][:160] if lines else "Summary unavailable."
            bullets = lines[1:6] if len(lines) > 6 else lines[1:6]
            voiceover = " ".join(lines[6:])[:600] if len(lines) > 6 else "In this POC..."
            return {"tldr": tldr, "bullets": bullets, "voiceover": voiceover}
        except Exception:
            pass

    # 3) Rule-based fallback
    steps = payload.get("steps_taken", [])
    bullets = []
    if payload.get("goal"): bullets.append(f"Goal: {payload['goal']}")
    if steps: bullets.append(f"Setup: {steps[0]}")
    if payload.get("issues"): bullets.append(f"Issue: {payload['issues'][0]}")
    if payload.get("fixes"): bullets.append(f"Fix: {payload['fixes'][0]}")
    if payload.get("outcome"): bullets.append(f"Result: {payload['outcome']}")
    while len(bullets) < 5: bullets.append("—")

    tldr = (payload.get("title") or "POC done")[:160]
    voiceover = "This quick POC demonstrates the setup, issues, fixes, and outcome."
    return {"tldr": tldr, "bullets": bullets[:5], "voiceover": voiceover}
