from __future__ import annotations

import os
from pathlib import Path
from typing import List

import mlflow.pyfunc
import numpy as np
import pandas as pd

FEATURES = [
    "origin_region",
    "destination_region",
    "carrier",
    "distance_km",
    "order_hour",
    "weekday",
    "priority",
    "historical_delay_rate",
]

_model = None
_model_root: Path | None = None


def _find_mlflow_model_root(model_dir: Path) -> Path:
    """Find the directory that contains the MLflow MLmodel file."""
    direct = model_dir / "MLmodel"
    if direct.exists():
        return model_dir

    matches = list(model_dir.rglob("MLmodel"))
    if not matches:
        raise FileNotFoundError(
            f"Could not find MLflow MLmodel under AZUREML_MODEL_DIR={model_dir}. "
            f"Top-level entries: {[p.name for p in model_dir.iterdir()]}"
        )

    # A registered MLflow model normally has exactly one MLmodel file.
    return matches[0].parent


def init() -> None:
    global _model, _model_root

    raw_model_dir = os.environ.get("AZUREML_MODEL_DIR")
    if not raw_model_dir:
        raise RuntimeError("AZUREML_MODEL_DIR is not set by Azure ML batch runtime.")

    model_dir = Path(raw_model_dir)
    print(f"[INIT] AZUREML_MODEL_DIR={model_dir}")

    _model_root = _find_mlflow_model_root(model_dir)
    print(f"[INIT] Loading MLflow model from {_model_root}")

    _model = mlflow.pyfunc.load_model(str(_model_root))
    print("[INIT] MLflow model loaded successfully")


def _to_risk_score(prediction) -> np.ndarray:
    """Normalize pyfunc predict output into P(delayed) risk scores."""
    if isinstance(prediction, pd.DataFrame):
        arr = prediction.to_numpy()
    elif isinstance(prediction, pd.Series):
        arr = prediction.to_numpy()
    else:
        arr = np.asarray(prediction)

    if arr.ndim == 2:
        if arr.shape[1] < 2:
            return arr[:, 0].astype(float)
        return arr[:, 1].astype(float)

    if arr.ndim == 1:
        return arr.astype(float)

    raise ValueError(f"Unexpected prediction shape: {arr.shape}")


def run(mini_batch: List[str]) -> pd.DataFrame:
    if _model is None:
        raise RuntimeError("Model has not been initialized.")

    print(f"[RUN] Processing {len(mini_batch)} input file(s)")
    output_frames: list[pd.DataFrame] = []

    for file_path in mini_batch:
        print(f"[RUN] Reading {file_path}")
        frame = pd.read_csv(file_path)

        missing = [column for column in FEATURES if column not in frame.columns]
        if missing:
            raise ValueError(
                f"Input file {file_path} is missing required features: {missing}. "
                f"Columns received: {list(frame.columns)}"
            )

        model_input = frame[FEATURES].copy()
        prediction = _model.predict(model_input)
        risk_score = _to_risk_score(prediction)

        if len(risk_score) != len(frame):
            raise ValueError(
                f"Prediction row count {len(risk_score)} does not match "
                f"input row count {len(frame)} for {file_path}."
            )

        result = pd.DataFrame(
            {
                "source_file": Path(file_path).name,
                "row_number": np.arange(len(frame), dtype=int),
                "risk_score": risk_score,
                "is_delayed_pred": (risk_score >= 0.5).astype(int),
            }
        )
        output_frames.append(result)

    if not output_frames:
        return pd.DataFrame(
            columns=["source_file", "row_number", "risk_score", "is_delayed_pred"]
        )

    result = pd.concat(output_frames, ignore_index=True)
    print(f"[RUN] Returning {len(result)} prediction row(s)")
    return result
