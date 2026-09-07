from __future__ import annotations

import os
from pathlib import Path

from azure.ai.ml.constants import BatchDeploymentOutputAction
from azure.ai.ml.entities import (
    AmlCompute,
    BatchEndpoint,
    BatchRetrySettings,
    CodeConfiguration,
    Environment,
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
)

from ml.azure_utils import get_ml_client, load_project_env

HERE = Path(__file__).resolve().parent
CONDA_FILE = HERE / "environment" / "conda.yaml"
CODE_DIR = HERE / "code"
BASE_IMAGE = "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04:latest"


def main() -> None:
    load_project_env()
    client = get_ml_client()

    model_name = os.getenv("AZUREML_MODEL_NAME", "shipment-delay-model")
    compute_name = os.getenv("AZUREML_BATCH_COMPUTE_NAME", "cpu-poc07")
    vm_size = os.getenv("AZUREML_BATCH_VM_SIZE", "Standard_DS2_v2")
    endpoint_name = os.getenv(
        "AZUREML_BATCH_ENDPOINT_NAME", "shipment-delay-batch-change-me"
    )
    deployment_name = os.getenv("AZUREML_BATCH_DEPLOYMENT_NAME", "blue-v2")
    environment_name = os.getenv(
        "AZUREML_BATCH_ENVIRONMENT_NAME", "poc07-batch-mlflow-py311"
    )

    if endpoint_name.endswith("change-me"):
        raise RuntimeError(
            "Change AZUREML_BATCH_ENDPOINT_NAME in .env; the endpoint name must be unique."
        )

    if not CONDA_FILE.exists():
        raise FileNotFoundError(f"Missing batch conda file: {CONDA_FILE}")
    if not (CODE_DIR / "batch_driver.py").exists():
        raise FileNotFoundError(f"Missing batch scoring script: {CODE_DIR / 'batch_driver.py'}")

    print("============================================")
    print(" Azure ML Batch Deployment - custom runtime")
    print("============================================")
    print(f"Model       : {model_name}")
    print(f"Compute     : {compute_name} ({vm_size})")
    print(f"Endpoint    : {endpoint_name}")
    print(f"Deployment  : {deployment_name}")
    print(f"Environment : {environment_name}")
    print(f"Base image  : {BASE_IMAGE}")
    print(f"Conda file  : {CONDA_FILE}")
    print(f"Score code  : {CODE_DIR / 'batch_driver.py'}")
    print("============================================")

    print(f"\n[1/4] Creating/reusing scale-to-zero compute {compute_name}")
    compute = AmlCompute(
        name=compute_name,
        size=vm_size,
        min_instances=0,
        max_instances=1,
        idle_time_before_scale_down=120,
    )
    client.begin_create_or_update(compute).result()
    print("[OK] Compute ready")

    print(f"\n[2/4] Creating/reusing batch endpoint {endpoint_name}")
    endpoint = BatchEndpoint(
        name=endpoint_name,
        description="POC-07 shipment delay batch endpoint",
    )
    client.batch_endpoints.begin_create_or_update(endpoint).result()
    print("[OK] Endpoint ready")

    print(f"\n[3/4] Preparing explicit Python 3.11 batch environment")
    environment = Environment(
        name=environment_name,
        description=(
            "POC-07 explicit MLflow batch runtime. Uses Python 3.11 to avoid "
            "auto-inferred image incompatibilities and includes azureml-core, "
            "which Azure ML batch scoring still requires."
        ),
        image=BASE_IMAGE,
        conda_file=str(CONDA_FILE),
    )

    model = client.models.get(name=model_name, label="latest")
    print(f"[OK] Using registered model: {model.name}:{model.version}")

    print(f"\n[4/4] Creating/updating deployment {deployment_name}")
    deployment = ModelBatchDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=model,
        compute=compute_name,
        environment=environment,
        code_configuration=CodeConfiguration(
            code=str(CODE_DIR),
            scoring_script="batch_driver.py",
        ),
        description=(
            "POC-07 custom batch deployment with explicit environment and scoring script"
        ),
        settings=ModelBatchDeploymentSettings(
            instance_count=1,
            max_concurrency_per_instance=1,
            mini_batch_size=1,
            output_action=BatchDeploymentOutputAction.APPEND_ROW,
            output_file_name="predictions.csv",
            retry_settings=BatchRetrySettings(max_retries=1, timeout=900),
            error_threshold=-1,
            logging_level="debug",
        ),
    )

    client.batch_deployments.begin_create_or_update(deployment).result()
    print("[OK] Deployment resource created/updated")

    endpoint = client.batch_endpoints.get(endpoint_name)
    endpoint.defaults.deployment_name = deployment_name
    client.batch_endpoints.begin_create_or_update(endpoint).result()

    print()
    print("[SUCCESS] Batch deployment is configured.")
    print(f"Endpoint   : {endpoint_name}")
    print(f"Deployment : {deployment_name}")
    print()
    print("IMPORTANT: the first invocation may still spend several minutes building")
    print("the custom environment image. In Studio, the BatchScoring node should no")
    print("longer use the previous auto-inferred environment.")


if __name__ == "__main__":
    main()
