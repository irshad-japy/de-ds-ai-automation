from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient

from .azure_utils import configure_tracking, load_project_env
from .common import OUTPUT_DIR, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the selected MLflow model in the active registry.")
    parser.add_argument("--tracking", choices=["local", "azure"], default="azure")
    parser.add_argument("--manifest", default=str(OUTPUT_DIR / "selected_model.json"))
    args = parser.parse_args()

    load_project_env()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest["tracking_mode"] != args.tracking:
        raise RuntimeError(
            f"Manifest was produced with tracking={manifest['tracking_mode']!r}, but you requested {args.tracking!r}. "
            "Train again with the same tracking mode before registering."
        )

    configure_tracking(args.tracking)
    model_name = os.getenv("AZUREML_MODEL_NAME", "shipment-delay-model")
    selected = manifest["selected"]
    version = mlflow.register_model(selected["model_uri"], model_name)

    client = MlflowClient()
    tags = {
        "poc": "07",
        "selected_model": selected["model_name"],
        "validation_roc_auc": f"{selected['metrics']['roc_auc']:.6f}",
        "validation_f1": f"{selected['metrics']['f1']:.6f}",
        "training_dataset_sha256": manifest["dataset_sha256"],
        "code_version": manifest["code_version"],
        "limitation": "Synthetic data; prediction probability is not causal certainty.",
    }
    for key, value in tags.items():
        client.set_model_version_tag(model_name, version.version, key, value)

    payload = {
        "model_name": model_name,
        "version": str(version.version),
        "source_run_id": selected["run_id"],
        "source_model_uri": selected["model_uri"],
        "tags": tags,
    }
    path = OUTPUT_DIR / "registered_model.json"
    write_json(path, payload)
    print(f"[OK] Registered model: {model_name} version {version.version}")
    print(f"[OK] Registration manifest: {path}")


if __name__ == "__main__":
    main()
