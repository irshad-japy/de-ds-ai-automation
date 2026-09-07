from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .common import SCORING_DIR, TRAIN_DIR, ensure_dirs

REGIONS = np.array(["north", "south", "east", "west", "central"])
CARRIERS = np.array(["carrier_a", "carrier_b", "carrier_c", "carrier_d"])
PRIORITIES = np.array(["standard", "express", "critical"])


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def build_dataset(rows: int = 2000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    origin = rng.choice(REGIONS, rows)
    destination = rng.choice(REGIONS, rows)
    carrier = rng.choice(CARRIERS, rows, p=[0.30, 0.27, 0.25, 0.18])
    priority = rng.choice(PRIORITIES, rows, p=[0.67, 0.25, 0.08])
    distance = np.clip(rng.gamma(shape=2.3, scale=420, size=rows), 40, 3500).round(1)
    order_hour = rng.integers(0, 24, rows)
    weekday = rng.integers(0, 7, rows)  # Monday=0 ... Sunday=6

    carrier_base = {"carrier_a": 0.10, "carrier_b": 0.17, "carrier_c": 0.22, "carrier_d": 0.29}
    historical = np.array([carrier_base[c] for c in carrier]) + rng.normal(0, 0.035, rows)
    historical = np.clip(historical, 0.02, 0.55).round(4)

    # Synthetic relationship only; it intentionally does not use post-delay information.
    logit = (
        -2.35
        + 3.8 * historical
        + 0.00048 * distance
        + 0.50 * (weekday >= 5)
        + 0.38 * ((order_hour <= 5) | (order_hour >= 21))
        + 0.50 * (priority == "critical")
        + 0.22 * (priority == "express")
        + 0.32 * (carrier == "carrier_d")
        + 0.18 * (origin == destination)
        + rng.normal(0, 0.20, rows)
    )
    probability = np.clip(_sigmoid(logit), 0.01, 0.95)
    delayed = rng.binomial(1, probability)

    return pd.DataFrame(
        {
            "shipment_id": [f"SHP-{i+1:06d}" for i in range(rows)],
            "origin_region": origin,
            "destination_region": destination,
            "carrier": carrier,
            "distance_km": distance,
            "order_hour": order_hour,
            "weekday": weekday,
            "priority": priority,
            "historical_delay_rate": historical,
            "is_delayed": delayed.astype(int),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic shipment-delay data.")
    parser.add_argument("--rows", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    ensure_dirs()
    df = build_dataset(args.rows, args.seed)
    train_path = TRAIN_DIR / "shipments.csv"
    df.to_csv(train_path, index=False)

    # Unlabelled scoring sample. It is deliberately a separate file/folder for batch inference.
    scoring = df.sample(n=min(40, len(df)), random_state=args.seed + 1).drop(columns=["is_delayed"])
    scoring_path = SCORING_DIR / "shipments_scoring.csv"
    scoring.to_csv(scoring_path, index=False)

    print(f"[OK] Training data: {train_path} ({len(df)} rows)")
    print(f"[OK] Scoring data:  {scoring_path} ({len(scoring)} rows)")
    print(f"[INFO] Delay rate: {df['is_delayed'].mean():.3f}")


if __name__ == "__main__":
    main()
