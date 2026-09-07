from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from azure.ai.ml import Input
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.exceptions import JobException

from ml.azure_utils import get_ml_client, load_project_env
from ml.common import FEATURES, OUTPUT_DIR, SCORING_DIR


def prepare_batch_input() -> Path:
    source = SCORING_DIR / "shipments_scoring.csv"

    if not source.exists():
        raise RuntimeError(
            "Scoring CSV does not exist. Run:\n"
            "poetry run python -m ml.generate_data"
        )

    df = pd.read_csv(source)

    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise RuntimeError(
            f"Batch input is missing required model features: {missing}"
        )

    # IMPORTANT:
    # Azure MLflow batch inference receives only the exact model features.
    batch_df = df[FEATURES].copy()

    batch_dir = OUTPUT_DIR / "batch_input"
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Delete old input files so an unsupported/stale file can't be submitted.
    for existing in batch_dir.iterdir():
        if existing.is_file():
            existing.unlink()

    batch_file = batch_dir / "shipments_batch.csv"
    batch_df.to_csv(batch_file, index=False)

    print("[OK] Prepared Azure batch input")
    print(f"     File   : {batch_file}")
    print(f"     Rows   : {len(batch_df)}")
    print(f"     Columns: {list(batch_df.columns)}")

    return batch_dir


def print_child_jobs(client, parent_job_name: str) -> None:
    print("\n[DIAGNOSTIC] Azure ML child jobs:")

    try:
        children = list(
            client.jobs.list(parent_job_name=parent_job_name)
        )

        if not children:
            print("  No child jobs returned yet.")
            return

        for child in children:
            print(
                f"  name={child.name} "
                f"display_name={child.display_name} "
                f"status={child.status}"
            )

            if child.services and "Studio" in child.services:
                print(
                    f"  Studio: "
                    f"{child.services['Studio'].endpoint}"
                )

    except Exception as exc:
        print(f"[WARN] Could not enumerate child jobs: {exc}")


def main():
    load_project_env()

    client = get_ml_client()

    endpoint_name = os.getenv(
        "AZUREML_BATCH_ENDPOINT_NAME",
        "shipment-delay-batch-change-me",
    )

    deployment_name = os.getenv(
        "AZUREML_BATCH_DEPLOYMENT_NAME",
        "blue",
    )

    batch_dir = prepare_batch_input()

    print()
    print("============================================")
    print(" Azure ML Batch Invocation")
    print("============================================")
    print(f"Endpoint   : {endpoint_name}")
    print(f"Deployment : {deployment_name}")
    print(f"Input      : {batch_dir}")
    print("============================================")

    job = client.batch_endpoints.invoke(
        endpoint_name=endpoint_name,

        # Explicit deployment avoids any default-routing ambiguity.
        deployment_name=deployment_name,

        input=Input(
            type=AssetTypes.URI_FOLDER,
            path=batch_dir.resolve(),
        ),
    )

    print(f"\n[OK] Batch job submitted: {job.name}")

    try:
        print("[INFO] Waiting for Azure batch scoring...")
        client.jobs.stream(job.name)

    except JobException:
        print()
        print("============================================")
        print("[FAILED] Azure batch child job failed")
        print("============================================")
        print(f"Parent job: {job.name}")

        print_child_jobs(client, job.name)

        print()
        print("Open this job with:")
        print(
            f"az ml job show --name {job.name} "
            "--resource-group rg-mlops-poc "
            "--workspace-name aml-mlops-poc-ws "
            "--web"
        )

        raise

    download = OUTPUT_DIR / "batch_download"
    download.mkdir(parents=True, exist_ok=True)

    client.jobs.download(
        name=job.name,
        output_name="score",
        download_path=str(download),
    )

    print()
    print("[SUCCESS] Azure batch scoring completed.")
    print(f"[OK] Batch output downloaded under: {download}")


if __name__ == "__main__":
    main()