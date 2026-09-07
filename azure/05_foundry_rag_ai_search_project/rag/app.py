from __future__ import annotations

import logging
import time
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from rag.config import settings
from rag.rag_engine import answer_question
from rag.retrieve import retrieve

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("poc05")

if settings.applicationinsights_connection_string:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(
            connection_string=settings.applicationinsights_connection_string
        )
        logger.info("Azure Monitor OpenTelemetry enabled")
    except Exception:
        logger.exception("Application Insights configuration failed; continuing with console logs")

app = FastAPI(
    title="POC-05 Foundry RAG + Azure AI Search",
    version="1.0.0",
    description="Beginner RAG POC exposing raw retrieval and grounded answer endpoints.",
)


class QueryRequest(BaseModel):
    query: str = Field(min_length=2)
    mode: Literal["vector", "hybrid"] = "hybrid"
    top_k: int = Field(default=5, ge=1, le=20)
    category: str | None = None


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    except Exception:
        logger.exception("request_failed path=%s", request.url.path)
        raise
    finally:
        logger.info(
            "http_request path=%s duration_ms=%.2f",
            request.url.path,
            (time.perf_counter() - start) * 1000,
        )


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "search_index": settings.azure_search_index_name,
        "search_auth_mode": settings.search_auth_mode,
        "foundry_auth_mode": settings.foundry_auth_mode,
    }


@app.post("/retrieve")
def retrieve_endpoint(body: QueryRequest) -> dict:
    try:
        rows = retrieve(body.query, body.mode, body.top_k, body.category)
        return {"count": len(rows), "results": [r.to_dict() for r in rows]}
    except Exception as exc:
        logger.exception("retrieve endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ask")
def ask_endpoint(body: QueryRequest) -> dict:
    try:
        result = answer_question(body.query, body.mode, body.top_k, body.category)
        return {
            "answer": result.answer,
            "sources": result.sources,
            "retrieval_mode": result.retrieval_mode,
            "latency_ms": round(result.latency_ms, 2),
        }
    except Exception as exc:
        logger.exception("ask endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
