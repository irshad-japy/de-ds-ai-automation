from typing import List, Tuple
import re

# Simple baseline extractors (replace with OpenAI/Cohere later)

def extract_takeaways_and_keywords(markdown_text: str, top_k: int = 7, kw_k: int = 15) -> tuple[list[str], list[str]]:
# naive sentence split
    sentences = re.split(r"(?<=[.!?])\s+", markdown_text)
    # pick longest/most informative-looking sentences
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    takeaways = sentences[:top_k]
    # keywords: pick distinct words by frequency
    words = re.findall(r"[A-Za-z][A-Za-z0-9_+-]{3,}", markdown_text)
    freq = {}
    for w in words:
        lw = w.lower()
        freq[lw] = freq.get(lw, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [w for w, _ in ranked if not w.startswith("http")][:kw_k]
    return takeaways, keywords

def build_hook_script(title: str, takeaways: List[str], max_seconds: int = 30) -> str:
# very short hook template
    core = "; ".join([t.split(".")[0] for t in takeaways[:3]])
    script = (
    f"If you want {title}, this video is for you. In under a minute, you'll learn: {core}. "
    f"Stick around—let's build it together."
    )
    return script