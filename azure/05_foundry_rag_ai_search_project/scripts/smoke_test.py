from __future__ import annotations

from rag.rag_engine import answer_question
from rag.retrieve import retrieve

QUERY = "What is the return window for damaged items?"


def main() -> None:
    print("1/3 Vector retrieval")
    vector = retrieve(QUERY, mode="vector", top_k=3)
    assert vector, "Vector retrieval returned no results"
    print("   top source:", vector[0].source)

    print("2/3 Hybrid retrieval")
    hybrid = retrieve(QUERY, mode="hybrid", top_k=3)
    assert hybrid, "Hybrid retrieval returned no results"
    print("   top source:", hybrid[0].source)

    print("3/3 Grounded generation")
    answer = answer_question(QUERY, mode="hybrid", top_k=5)
    assert answer.answer, "RAG answer is empty"
    print("   answer:", answer.answer)

    print("\nSMOKE TEST PASSED")


if __name__ == "__main__":
    main()
