from typing import List
import re

def simple_chunk(text: str, max_len: int = 1200) -> List[str]:
    # naive splitter at paragraph boundaries
    paras = re.split(r"\n\s*\n", text.strip())
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 1 <= max_len:
            buf += ("\n\n" if buf else "") + p
        else:
            if buf:
                chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    return chunks
