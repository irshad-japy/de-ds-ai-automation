from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import OUTPUT_DIR


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(OUTPUT_DIR / "selected_model.json"))
    args = parser.parse_args()
    payload = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

    print("MODEL COMPARISON")
    print("=" * 92)
    print(f"{'model':24} {'roc_auc':>10} {'f1':>10} {'precision':>10} {'recall':>10} {'run_id':>18}")
    for r in payload["all_runs"]:
        m = r["metrics"]
        print(f"{r['model_name']:24} {m['roc_auc']:10.4f} {m['f1']:10.4f} {m['precision']:10.4f} {m['recall']:10.4f} {r['run_id'][:18]:>18}")
    print("=" * 92)
    print(f"Selected: {payload['selected']['model_name']} ({payload['selection_rule']})")


if __name__ == "__main__":
    main()
