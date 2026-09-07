from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time

from rag.config import PROJECT_ROOT, settings
from rag.rag_engine import answer_question
from rag.retrieve import retrieve


def main() -> None:
    questions_path = PROJECT_ROOT / "eval" / "questions.json"
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    rows = []

    for q in questions:
        print(f"\n[{q['id']}] {q['question']}")
        started = time.perf_counter()
        retrieved = retrieve(q["question"], mode="hybrid", top_k=settings.top_k)
        retrieval_latency_ms = (time.perf_counter() - started) * 1000

        returned_sources = [r.source for r in retrieved]
        expected = q.get("expected_source")
        hit = True if expected is None else expected in returned_sources

        rag = answer_question(q["question"], mode="hybrid", top_k=settings.top_k)
        answer_lower = rag.answer.lower()
        unsupported = bool(q.get("unsupported"))
        fallback = "i don't have enough information" in answer_lower
        unsupported_answer = unsupported and not fallback

        citation_correct = True if expected is None else any(
            src.startswith(f"{expected}#") for src in rag.sources
        )
        answer_grounded_heuristic = (fallback if unsupported else (hit and citation_correct))

        row = {
            "id": q["id"],
            "question": q["question"],
            "expected_source": expected,
            "returned_sources": returned_sources,
            "retrieval_hit_at_k": hit,
            "citation_correct": citation_correct,
            "answer_grounded_heuristic": answer_grounded_heuristic,
            "unsupported_answer": unsupported_answer,
            "retrieval_latency_ms": round(retrieval_latency_ms, 2),
            "end_to_end_latency_ms": round(rag.latency_ms, 2),
            "answer": rag.answer,
        }
        rows.append(row)
        print(json.dumps({k: row[k] for k in ["retrieval_hit_at_k", "citation_correct", "answer_grounded_heuristic", "unsupported_answer"]}, indent=2))

    summary = {
        "questions": len(rows),
        "retrieval_hit_at_k_rate": sum(r["retrieval_hit_at_k"] for r in rows) / len(rows),
        "citation_correct_rate": sum(r["citation_correct"] for r in rows) / len(rows),
        "answer_grounded_heuristic_rate": sum(r["answer_grounded_heuristic"] for r in rows) / len(rows),
        "unsupported_answer_rate": sum(r["unsupported_answer"] for r in rows) / len(rows),
        "avg_end_to_end_latency_ms": round(statistics.mean(r["end_to_end_latency_ms"] for r in rows), 2),
    }

    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "top_k": settings.top_k,
        "summary": summary,
        "rows": rows,
    }

    out_dir = PROJECT_ROOT / "eval" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = out_dir / f"eval_{stamp}.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nSUMMARY")
    print(json.dumps(summary, indent=2))
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
