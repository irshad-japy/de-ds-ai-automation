import logging
from fastapi import FastAPI
from .schemas import IngestRequest, AskRequest, AskResponse
from ..logging_setup import setup_logging
from ..io.readers import gather_input
from ..rag.retrieve import index_texts
from ..rag.answer import answer
from pydantic import BaseModel

class AskRequest(BaseModel):
    query: str
    ext: str | None = None  # ".pdf", ".csv", ".md", ".txt"
    
setup_logging()
log = logging.getLogger("lr.api")

app = FastAPI(title="Local RAG API", version="0.1.0")

@app.get("/health")
def health():
    log.info("health-check")
    return {"ok": True}

@app.post("/ingest")
def ingest(req: IngestRequest):
    pairs = gather_input(req.folder)
    res = index_texts(pairs)
    log.info(f"ingested folder={req.folder} chunks={res['chunks_indexed']}")
    return {"folder": req.folder, **res}

@app.post("/ask")
def ask(req: AskRequest):
    res = answer(req.query, only_ext=req.ext)
    return res
