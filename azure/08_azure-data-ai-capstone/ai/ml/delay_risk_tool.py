from __future__ import annotations

import os


def score_delay_risk(distance_km: float, backlog: int, weather_score: float) -> dict:
    """Safe read-only scoring interface for optional POC-07 integration."""
    model_uri = os.getenv("MLFLOW_MODEL_URI", "").strip()
    if model_uri:
        try:
            import mlflow.pyfunc
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError("Run: poetry install --with ml") from exc
        model = mlflow.pyfunc.load_model(model_uri)
        frame = pd.DataFrame([{"distance_km": distance_km, "backlog": backlog, "weather_score": weather_score}])
        pred = model.predict(frame)
        return {"risk_score": float(pred[0]), "source": model_uri}

    # Offline deterministic fallback for capstone wiring tests only.
    risk = min(1.0, 0.0015 * distance_km + 0.03 * backlog + 0.25 * weather_score)
    return {"risk_score": round(risk, 4), "source": "offline-demo-heuristic"}


if __name__ == "__main__":
    print(score_delay_risk(450, 6, 0.3))
