from __future__ import annotations

import argparse
import os
from pathlib import Path

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Data

from .azure_utils import get_ml_client, load_project_env
from .common import TRAIN_DIR, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload/register the synthetic CSV as an Azure ML data asset.")
    parser.add_argument("--data", default=str(TRAIN_DIR / "shipments.csv"))
    args = parser.parse_args()

    path = Path(args.data).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Generate data first: {path}")

    load_project_env()
    name = os.getenv("AZUREML_DATA_ASSET_NAME", "shipment-delay-synthetic")
    version = sha256_file(path)[:12]
    client = get_ml_client()

    asset = Data(
        name=name,
        version=version,
        description="Synthetic shipment-delay training data for POC-07.",
        path=str(path),
        type=AssetTypes.URI_FILE,
        tags={"poc": "07", "sha256": sha256_file(path)},
    )
    result = client.data.create_or_update(asset)
    print(f"[OK] Registered data asset: {result.name}:{result.version}")
    print(f"[INFO] Azure ML uploaded the local file to workspace-managed Azure Storage.")


if __name__ == "__main__":
    main()
