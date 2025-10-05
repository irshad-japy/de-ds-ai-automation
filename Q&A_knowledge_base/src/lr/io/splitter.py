def split_text(text: str, max_len: int = 900, overlap: int = 120):
    chunks, i, n = [], 0, len(text)
    step = max_len - overlap
    while i < n:
        chunks.append(text[i:i+max_len])
        i += step
    return [c.strip() for c in chunks if c.strip()]
