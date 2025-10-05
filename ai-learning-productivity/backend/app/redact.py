import re
from typing import List, Dict, Any
SENSITIVE_PATTERNS = [
    r"sk-[A-Za-z0-9]{10,}",         # API-like
    r"AKIA[0-9A-Z]{16}",            # AWS key
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"\b\d{1,3}(\.\d{1,3}){3}\b",   # IP
    r"[A-Za-z]:\\[^\n\r]*",         # Windows path
    r"(?i)password\s*=\s*.+",
    r"(?i)token\s*=\s*.+",
]
def sensitive_hits(text: str, extra: List[str]) -> List[str]:
    hits = []
    for pat in SENSITIVE_PATTERNS + [re.escape(x) for x in extra]:
        if re.search(pat, text):
            hits.append(pat)
    return list(set(hits))
