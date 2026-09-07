from __future__ import annotations

import argparse

from azure.ai.projects import AIProjectClient

from ai.rag.query_search import retrieve
from common.auth import get_token_credential
from common.config import Settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", default="When is a shipment considered delayed?")
    args = parser.parse_args()
    s = Settings()
    if not s.foundry_project_endpoint:
        raise RuntimeError("Set FOUNDRY_PROJECT_ENDPOINT")
    sources = retrieve(args.question, 3)
    context = "\n\n".join(
        f"SOURCE={x['source']}\nTITLE={x['title']}\nCONTENT={x['content']}" for x in sources
    )
    prompt = f"""
You are a grounded Azure Data + AI capstone assistant.
Answer ONLY from the supplied context. If the context is insufficient, say that the answer is unsupported.
Cite every factual claim with the source in square brackets, for example [policy-shipping.md].

QUESTION:
{args.question}

CONTEXT:
{context}
"""
    project = AIProjectClient(endpoint=s.foundry_project_endpoint, credential=get_token_credential())
    openai = project.get_openai_client()
    response = openai.responses.create(model=s.foundry_model, input=prompt)
    print(response.output_text)
    print("\nRetrieved sources:")
    for source in sources:
        print(" -", source["source"])


if __name__ == "__main__":
    main()
