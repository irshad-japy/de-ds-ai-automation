def enhance_prompt(prompt: str, enhance: bool = True) -> str:
    extras = "cinematic, 8k, photorealistic, ultra-detailed, high contrast, dramatic lighting"
    if enhance and prompt:
        return f"{prompt}, {extras}"
    return prompt or ""

def split_into_sentences(text: str):
    # Very small splitter; avoids heavy NLP dep
    import re
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]
