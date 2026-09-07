# Azure CLI authentication (recommended for this local POC)

Use `AZURE_AUTH_MODE=cli` after `az login`. The patched helper explicitly uses `AzureCliCredential`. If a browser still opens, verify which copy of the module is being imported with `poetry run python -c "import ml.azure_utils as a; print(a.__file__)"`.

# Troubleshooting

## `az is not recognized`
For the local Windows flow, Azure CLI authentication is recommended because it uses the same account you already verified with `az ml workspace show`. Set `AZURE_AUTH_MODE=cli`.

## Browser opens but Azure access is denied
Confirm the signed-in account has access to the subscription/resource group/workspace. A Contributor-like role on the POC resource group/workspace is the simplest learning setup.

## `No module named azure` / `No module named mlflow`
From the project root run `poetry env use 3.12` and `poetry install`. Verify with `poetry run python --version` and `poetry show`. `requirements.txt` is only a fallback.

## MLflow 404 / logged-model API mismatch
Use the provided `mlflow==2.22.5` pin. Do not casually upgrade this POC to MLflow 3.x while using Azure ML workspace tracking unless you validate Azure ML support for that client/server combination.

## Batch compute quota / VM size unavailable
Change `AZUREML_BATCH_VM_SIZE` in `.env` to an allowed small CPU SKU in your region. Keep `min_instances=0`, `max_instances=1` for the demo.

## Batch endpoint name already exists
Batch endpoint names must be unique within an Azure region. Change `AZUREML_BATCH_ENDPOINT_NAME` to a unique value such as `shipment-delay-batch-irshad-0906`.

## Batch deployment fails on schema/input
First verify local scoring works. Ensure the batch input folder contains CSV files with exactly the eight expected feature columns. The logged MLflow pyfunc is configured to call `predict_proba`.

## Model registration fails
Train with `--tracking azure` first. A manifest from local tracking points to local `mlruns` and cannot be registered into a different Azure tracking server by this beginner workflow.
