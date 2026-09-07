# POC-07 Batch Endpoint — `Image build failed` fix

## What the failure means

If Azure ML Studio shows **BatchScoring → Image build failed** and points to
`azureml-logs/20_image_build_log.txt`, the scoring container failed before the
CSV was scored. Changing `invoke_batch.py` input columns does not fix this stage.

This project now uses an explicit batch environment and an explicit scoring
script instead of relying on Azure ML to infer a serving image from the MLflow
model artifact.

## Why Python 3.11 is used remotely

The local POC can remain on Poetry/Python 3.12. The batch serving environment is
separate. It is pinned to Python 3.11 and includes `azureml-core`, which Azure ML
batch scoring still requires for the batch runtime. This avoids the risky edge
where an MLflow model logged from Python 3.12 is combined with legacy batch
runtime dependencies during automatic image generation.

## Files

- `azure/batch/environment/conda.yaml`
- `azure/batch/code/batch_driver.py`
- `azure/batch/deploy_batch.py`
- `azure/batch/invoke_batch.py`

## Required `.env` values

Keep your existing endpoint name and use a fresh deployment name:

```text
AZUREML_BATCH_ENDPOINT_NAME=shipment-delay-batch-1fe672c
AZUREML_BATCH_DEPLOYMENT_NAME=blue-v2
AZUREML_BATCH_ENVIRONMENT_NAME=poc07-batch-mlflow-py311
```

## Run

```bat
poetry run python azure\batch\deploy_batch.py
poetry run python azure\batch\invoke_batch.py
```

## If the image still fails

Open the failed BatchScoring node → **Outputs + logs** →
`azureml-logs/20_image_build_log.txt`.

Or download the child job logs:

```bat
az ml job list ^
  --parent-job-name <PARENT_JOB_NAME> ^
  --resource-group rg-mlops-poc ^
  --workspace-name aml-mlops-poc-ws ^
  --query "[].{Name:name,DisplayName:display_name,Status:status}" -o table

az ml job download ^
  --name <CHILD_JOB_NAME> ^
  --resource-group rg-mlops-poc ^
  --workspace-name aml-mlops-poc-ws ^
  --all ^
  --download-path outputs\azure_job_logs
```

Then inspect `20_image_build_log.txt` for the first package-resolution or image
build error. Do not diagnose from the final `PipelineHasStepJobFailed` line;
that line is only the parent pipeline reporting the child failure.
