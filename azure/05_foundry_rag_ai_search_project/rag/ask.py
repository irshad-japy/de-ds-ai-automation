from __future__ import annotations

import argparse
from rag.config import settings
from rag.rag_engine import answer_question


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a grounded RAG question")
    parser.add_argument("--query", required=True)
    parser.add_argument("--mode", choices=["vector", "hybrid"], default="hybrid")
    parser.add_argument("--top-k", type=int, default=settings.top_k)
    parser.add_argument("--category", default=None)
    args = parser.parse_args()

    result = answer_question(args.query, args.mode, args.top_k, args.category)
    print("\nANSWER\n------")
    print(result.answer)
    print("\nRETRIEVED SOURCES\n-----------------")
    for src in result.sources:
        print(f"- {src}")
    print(f"\nLatency: {result.latency_ms:.2f} ms")


if __name__ == "__main__":
    main()
