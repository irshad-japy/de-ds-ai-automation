from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from rag.documents import SourceDocument


@dataclass
class Chunk:
    id: str
    title: str
    content: str
    source: str
    category: str
    chunk_id: str
    effective_date: str


def _tokenize(text: str) -> tuple[list[int] | list[str], object | None]:
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return enc.encode(text), enc
    except Exception:
        return re.findall(r"\S+", text), None


def _decode(tokens, encoder) -> str:
    if encoder is not None:
        return encoder.decode(tokens)
    return " ".join(tokens)


def chunk_document(doc: SourceDocument, chunk_size: int, overlap: int) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    tokens, encoder = _tokenize(doc.content)
    step = chunk_size - overlap
    chunks: list[Chunk] = []

    for idx, start in enumerate(range(0, len(tokens), step), start=1):
        token_slice = tokens[start : start + chunk_size]
        if not token_slice:
            break
        text = _decode(token_slice, encoder).strip()
        if not text:
            continue

        chunk_id = f"{doc.source.rsplit('.', 1)[0]}-{idx:04d}"
        stable = hashlib.sha1(f"{doc.source}:{chunk_id}".encode("utf-8")).hexdigest()[:24]
        chunks.append(
            Chunk(
                id=stable,
                title=doc.title,
                content=text,
                source=doc.source,
                category=doc.category,
                chunk_id=chunk_id,
                effective_date=str(doc.metadata.get("effective_date") or ""),
            )
        )

        if start + chunk_size >= len(tokens):
            break
    return chunks


def chunk_documents(docs: list[SourceDocument], chunk_size: int, overlap: int) -> list[Chunk]:
    output: list[Chunk] = []
    for doc in docs:
        output.extend(chunk_document(doc, chunk_size, overlap))
    return output
