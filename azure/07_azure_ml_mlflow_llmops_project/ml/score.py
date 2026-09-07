from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import mlflow.sklearn
import pandas as pd

from .azure_utils import configure_tracking
from .common import OUTPUT_DIR, SCORING_DIR, require_columns, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a CSV with the selected model and emit risk_score.")
    parser.add_argument("--tracking", choices=["local", "azure"], default="local")
    parser.add_argument("--manifest", default=str(OUTPUT_DIR / "selected_model.json"))
    parser.add_argument("--input", default=str(SCORING_DIR / "shipments_scoring.csv"))
    parser.add_argument("--output", default=str(OUTPUT_DIR / "predictions.csv"))
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest["tracking_mode"] != args.tracking:
        raise RuntimeError("Use the same --tracking mode that created selected_model.json.")
    configure_tracking(args.tracking)

    frame = pd.read_csv(args.input)
    require_columns(frame.columns)
    model = mlflow.sklearn.load_model(manifest["selected"]["model_uri"])

    started = time.perf_counter()
    probability = model.predict_proba(frame[manifest["feature_list"]])[:, 1]
    elapsed = time.perf_counter() - started

    out = pd.DataFrame()
    if "shipment_id" in frame.columns:
        out["shipment_id"] = frame["shipment_id"]
    out["risk_score"] = probability
    out["is_delayed_pred"] = (probability >= 0.5).astype(int)
    out["risk_band"] = pd.cut(
        probability,
        bins=[-0.001, 0.30, 0.60, 1.001],
        labels=["low", "medium", "high"],
    ).astype(str)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    metrics = {
        "rows_scored": len(out),
        "total_scoring_seconds": elapsed,
        "mean_latency_ms_per_row": (elapsed * 1000 / max(1, len(out))),
        "prediction_positive_rate": float(out["is_delayed_pred"].mean()),
        "risk_score_mean": float(out["risk_score"].mean()),
        "risk_score_p95": float(out["risk_score"].quantile(0.95)),
        "source_model": manifest["selected"]["model_name"],
    }
    write_json(OUTPUT_DIR / "scoring_metrics.json", metrics)
    print(f"[OK] Wrote {len(out)} predictions: {output_path}")
    print(f"[INFO] Mean risk score={metrics['risk_score_mean']:.4f}; mean latency={metrics['mean_latency_ms_per_row']:.3f} ms/row")


if __name__ == "__main__":
    main()
