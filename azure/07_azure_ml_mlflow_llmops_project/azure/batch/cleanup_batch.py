from __future__ import annotations

import os
from ml.azure_utils import get_ml_client, load_project_env


def main():
    load_project_env()
    client = get_ml_client()
    endpoint = os.getenv("AZUREML_BATCH_ENDPOINT_NAME", "")
    compute = os.getenv("AZUREML_BATCH_COMPUTE_NAME", "")

    if endpoint and not endpoint.endswith("change-me"):
        print(f"[DELETE] Batch endpoint: {endpoint}")
        client.batch_endpoints.begin_delete(name=endpoint).result()
    if compute:
        print(f"[DELETE] Compute: {compute}")
        client.compute.begin_delete(name=compute).result()
    print("[OK] Batch serving resources deleted. Registered model/data/workspace remain.")


if __name__ == "__main__":
    main()
