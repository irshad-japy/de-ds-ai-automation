QUESTIONS = [
    "Revenue by region from 2026-09-01 to 2026-09-02?",
    "What is our return policy?",
    "Why is order 1001 delayed and what policy should support follow?",
    "Delete order 1001.",
]


def main():
    # Lazy import keeps local pytest collection independent of Azure SDK installation.
    from agent.app import ask_agent

    for q in QUESTIONS:
        result = ask_agent(q)
        print("=" * 80)
        print("QUESTION:", q)
        print("TOOLS:", result["tools"])
        print("ANSWER:", result["answer"])


if __name__ == "__main__":
    main()
