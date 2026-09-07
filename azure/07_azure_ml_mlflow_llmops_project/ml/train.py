from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, log_loss, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .azure_utils import configure_tracking, load_project_env
from .common import (
    CATEGORICAL_FEATURES,
    FEATURES,
    NUMERIC_FEATURES,
    OUTPUT_DIR,
    TARGET,
    TRAIN_DIR,
    ensure_dirs,
    git_code_version,
    require_columns,
    sha256_file,
    write_json,
)


def make_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ],
        remainder="drop",
    )


def build_models(seed: int):
    return {
        "logistic_regression": Pipeline(
            [
                ("preprocess", make_preprocessor()),
                ("model", LogisticRegression(max_iter=1000, C=1.0, random_state=seed)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("preprocess", make_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=8,
                        min_samples_leaf=3,
                        random_state=seed,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def metric_dict(y_true, probability):
    pred = (probability >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "log_loss": float(log_loss(y_true, np.c_[1 - probability, probability], labels=[0, 1])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train two shipment-delay models and track them with MLflow.")
    parser.add_argument("--tracking", choices=["local", "azure"], default="local")
    parser.add_argument("--data", default=str(TRAIN_DIR / "shipments.csv"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.20)
    args = parser.parse_args()

    ensure_dirs()
    load_project_env()
    data_path = Path(args.data).resolve()
    if not data_path.exists():
        raise FileNotFoundError("Training CSV not found. Run: python -m ml.generate_data")

    df = pd.read_csv(data_path)
    require_columns(df.columns)
    if TARGET not in df.columns:
        raise ValueError(f"Missing target column: {TARGET}")

    X = df[FEATURES].copy()
    y = df[TARGET].astype(int)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )

    tracking_uri = configure_tracking(args.tracking)
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "poc07-shipment-delay")
    mlflow.set_experiment(experiment_name)

    dataset_hash = sha256_file(data_path)
    code_version = git_code_version()
    results = []

    for model_name, model in build_models(args.seed).items():
        run_name = f"{model_name}-seed-{args.seed}"
        with mlflow.start_run(run_name=run_name) as run:
            started = time.perf_counter()
            model.fit(X_train, y_train)
            train_seconds = time.perf_counter() - started
            prob = model.predict_proba(X_val)[:, 1]
            metrics = metric_dict(y_val, prob)
            metrics["train_seconds"] = float(train_seconds)

            params = {
                "model_name": model_name,
                "seed": args.seed,
                "test_size": args.test_size,
                "train_rows": len(X_train),
                "validation_rows": len(X_val),
                "dataset_sha256": dataset_hash,
                "feature_count": len(FEATURES),
            }
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.set_tags(
                {
                    "poc": "07",
                    "problem": "synthetic-shipment-delay",
                    "code_version": code_version,
                    "leakage_review": "passed-feature-list-review",
                    "tracking_mode": args.tracking,
                }
            )
            mlflow.log_text(json.dumps(FEATURES, indent=2), "metadata/features.json")
            mlflow.log_text(code_version, "metadata/code_version.txt")
            mlflow.log_text(dataset_hash, "metadata/training_dataset_sha256.txt")

            # Make the generic MLflow pyfunc endpoint return predict_proba output.
            # Column 0 = P(not delayed); column 1 = P(delayed) = risk_score.
            example = X_train.head(5)
            signature = infer_signature(example, model.predict_proba(example))
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                signature=signature,
                input_example=example,
                pyfunc_predict_fn="predict_proba",
                metadata={
                    "risk_score_column": 1,
                    "feature_list": FEATURES,
                    "dataset_sha256": dataset_hash,
                },
            )

            record = {
                "model_name": model_name,
                "run_id": run.info.run_id,
                "model_uri": f"runs:/{run.info.run_id}/model",
                "metrics": metrics,
            }
            results.append(record)
            print(f"[OK] {model_name}: run={run.info.run_id} roc_auc={metrics['roc_auc']:.4f} f1={metrics['f1']:.4f}")

    selected = max(results, key=lambda r: (r["metrics"]["roc_auc"], r["metrics"]["f1"]))
    manifest = {
        "tracking_mode": args.tracking,
        "tracking_uri": tracking_uri,
        "experiment_name": experiment_name,
        "data_path": str(data_path),
        "dataset_sha256": dataset_hash,
        "code_version": code_version,
        "feature_list": FEATURES,
        "all_runs": results,
        "selected": selected,
        "selection_rule": "highest validation roc_auc; f1 used as tie-breaker",
        "limitations": [
            "Synthetic training data is for workflow demonstration only.",
            "Probability is predictive, not a causal explanation of delay.",
            "Monitor distribution shift and data freshness before production use.",
        ],
    }
    manifest_path = OUTPUT_DIR / "selected_model.json"
    write_json(manifest_path, manifest)
    print(f"[SELECTED] {selected['model_name']} with ROC AUC {selected['metrics']['roc_auc']:.4f}")
    print(f"[OK] Selection manifest: {manifest_path}")


if __name__ == "__main__":
    main()
