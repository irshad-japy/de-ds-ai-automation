from pathlib import Path
from pypdf import PdfReader
import pandas as pd
from unstructured.partition.auto import partition
from .splitter import split_text

def read_any(path: Path) -> list[str]:
    suf = path.suffix.lower()
    if suf == ".pdf":
        reader = PdfReader(str(path))
        txt = "\n".join([p.extract_text() or "" for p in reader.pages])
        return split_text(txt)

    if suf in {".md", ".txt"}:
        return split_text(path.read_text(encoding="utf-8", errors="ignore"))

    if suf == ".csv":
        # Keep CSV intact per file (useful for “structured” questions)
        df = pd.read_csv(path)
        # Convert small CSV to markdown-like preview; large CSV gets head()
        if len(df) > 2000:
            df = df.head(2000)
        return [df.to_csv(index=False)]

    # Fallback to unstructured for html/docx/others
    els = partition(filename=str(path))
    text = "\n".join(getattr(e, "text", "") for e in els if getattr(e, "text", None))
    return split_text(text)

def gather_input(folder: str) -> list[tuple[str, str]]:
    base = Path(folder)
    files = [p for p in base.rglob("*") if p.is_file()]
    out: list[tuple[str, str]] = []
    for p in files:
        for idx, chunk in enumerate(read_any(p)):
            out.append((f"{p.name}::{idx}", chunk))
    return out
