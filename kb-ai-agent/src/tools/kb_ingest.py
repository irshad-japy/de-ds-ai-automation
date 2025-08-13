import os, glob
from typing import List, Dict
from dotenv import load_dotenv; load_dotenv()
from unstructured.partition.pdf import partition_pdf
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from ..util.chunking import simple_chunk

INDEX_DIR = os.getenv("INDEX_DIR", "./data/index")
EMB = embedding_functions.DefaultEmbeddingFunction()  # uses sentence-transformers via API-free default

def _ensure_collection(client, name="kb"):
    try:
        return client.get_collection(name)
    except:
        return client.create_collection(name)

def ingest_pdfs(paths: List[str]):
    client = PersistentClient(path=INDEX_DIR)
    kb = _ensure_collection(client)

    docs, ids, metas = [], [], []
    for path in paths:
        elements = partition_pdf(filename=path)
        text = "\n".join([e.text for e in elements if getattr(e, "text", None)])
        for i, chunk in enumerate(simple_chunk(text)):
            docs.append(chunk)
            ids.append(f"{os.path.basename(path)}::{i}")
            metas.append({"source": path, "type": "pdf"})
    if docs:
        kb.add(documents=docs, metadatas=metas, ids=ids, embedding_function=EMB)

def ingest_text_blobs(items: List[Dict]):
    """items: [{text: "...", source: "url-or-note"}]"""
    client = PersistentClient(path=INDEX_DIR)
    kb = _ensure_collection(client)
    docs, ids, metas = [], [], []
    for i, it in enumerate(items):
        for j, chunk in enumerate(simple_chunk(it["text"])):
            docs.append(chunk)
            ids.append(f"{i}::{j}")
            metas.append({"source": it.get("source", "ad-hoc"), "type":"text"})
    if docs:
        kb.add(documents=docs, metadatas=metas, ids=ids, embedding_function=EMB)
