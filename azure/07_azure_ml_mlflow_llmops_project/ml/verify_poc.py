from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .azure_utils import configure_tracking
from .common import FEATURES, OUTPUT_DIR, TRAIN_DIR


def check(condition: bool, ok: str, fail: str, failures: list[str]):
    if condition:
        print(f"[PASS] {ok}")
    else:
        print(f"[FAIL] {fail}")
        failures.append(fail)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify POC-07 outputs against the source validation checklist.")
    parser.add_argument("--tracking", choices=["local", "azure"], default="local")
    parser.add_argument("--check-registry", action="store_true")
    args = parser.parse_args()

    failures = []
    train = TRAIN_DIR / "shipments.csv"
    selected_path = OUTPUT_DIR / "selected_model.json"
    pred_path = OUTPUT_DIR / "predictions.csv"
    reg_path = OUTPUT_DIR / "registered_model.json"

    check(train.exists(), "Synthetic training data exists", "Training data is missing", failures)
    if train.exists():
        df = pd.read_csv(train)
        check(all(c in df.columns for c in FEATURES + ["is_delayed"]), "All required features and label exist", "Required columns are missing", failures)

    check(selected_path.exists(), "Model selection manifest exists", "selected_model.json is missing", failures)
    if selected_path.exists():
        manifest = json.loads(selected_path.read_text(encoding="utf-8"))
        check(len(manifest.get("all_runs", [])) >= 2, "At least two MLflow runs were logged", "Fewer than two tracked runs", failures)
        check(bool(manifest.get("selected", {}).get("run_id")), "A selected run is recorded", "No selected run recorded", failures)
        check(set(manifest.get("feature_list", [])) == set(FEATURES), "Feature list matches leakage-reviewed design", "Feature list differs from approved features", failures)

    check(pred_path.exists(), "A scoring path produced predictions", "predictions.csv is missing", failures)
    if pred_path.exists():
        preds = pd.read_csv(pred_path)
        check("risk_score" in preds.columns, "risk_score is present", "risk_score is missing", failures)
        if "risk_score" in preds:
            check(preds["risk_score"].between(0, 1).all(), "risk_score is within [0, 1]", "risk_score has invalid values", failures)

    if args.check_registry:
        check(reg_path.exists(), "Registration manifest exists", "registered_model.json is missing", failures)
        if reg_path.exists():
            from mlflow.tracking import MlflowClient
            configure_tracking(args.tracking)
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
            mv = MlflowClient().get_model_version(reg["model_name"], reg["version"])
            check(str(mv.version) == str(reg["version"]), "Registered model version is queryable", "Could not verify registered model version", failures)

    leakage_doc = Path(__file__).resolve().parents[1] / "docs" / "data_leakage_check.md"
    check(leakage_doc.exists(), "Leakage review is documented", "Leakage review document is missing", failures)

    print("\nRESULT:", "PASS" if not failures else "FAIL")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
