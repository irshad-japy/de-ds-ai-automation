from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any
import yaml


@dataclass
class SourceDocument:
    title: str
    source: str
    category: str
    content: str
    metadata: dict[str, Any]


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


def parse_markdown_document(path: Path) -> SourceDocument:
    raw = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(raw)
    if match:
        metadata = yaml.safe_load(match.group(1)) or {}
        content = match.group(2).strip()
    else:
        metadata = {}
        content = raw.strip()

    title = str(metadata.get("title") or path.stem.replace("_", " ").title())
    source = str(metadata.get("source") or path.name)
    category = str(metadata.get("category") or "uncategorized")
    return SourceDocument(
        title=title,
        source=source,
        category=category,
        content=content,
        metadata=metadata,
    )


def load_documents(directory: Path) -> list[SourceDocument]:
    paths = sorted([*directory.glob("*.md"), *directory.glob("*.txt")])
    if not paths:
        raise FileNotFoundError(f"No .md or .txt documents found in {directory}")
    return [parse_markdown_document(p) for p in paths]
