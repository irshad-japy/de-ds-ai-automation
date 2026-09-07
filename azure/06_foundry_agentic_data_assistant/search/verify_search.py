from __future__ import annotations

import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def main():
    client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.getenv("SEARCH_INDEX_NAME", "poc06-policy-index"),
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"]),
    )
    rows = list(client.search("return eligibility", top=3, select=["id", "title", "content", "url"]))
    if not rows:
        raise SystemExit("[FAIL] Search returned zero rows")
    print("[SUCCESS] Search returned results")
    for row in rows:
        print(f"- {row['id']}: {row['title']}")

if __name__ == "__main__":
    main()
