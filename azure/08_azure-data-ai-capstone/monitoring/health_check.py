from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def age_seconds(path: Path) -> float | None:
    if not path.exists():
        return None
    return (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime)


def main() -> None:
    checks = {
        "gold_summary": Path("output/gold/gold_summary.json"),
        "search_documents": Path("output/search/documents.json"),
        "document_intelligence": Path("output/document_intelligence/invoice_001_result.json"),
    }
    report = {name: {"exists": p.exists(), "age_seconds": age_seconds(p)} for name, p in checks.items()}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
