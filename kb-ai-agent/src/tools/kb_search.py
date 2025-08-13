import os
from chromadb import PersistentClient
from chromadb.utils import embedding_functions

INDEX_DIR = os.getenv("INDEX_DIR", "./data/index")
EMB = embedding_functions.DefaultEmbeddingFunction()

def search_kb(query: str, k: int = 5):
    client = PersistentClient(path=INDEX_DIR)
    kb = client.get_collection("kb")
    res = kb.query(query_texts=[query], n_results=k, embedding_function=EMB)
    # returns {documents: [[...]], metadatas: [[...]], ids: [[...]]}
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    return list(zip(docs, metas))
