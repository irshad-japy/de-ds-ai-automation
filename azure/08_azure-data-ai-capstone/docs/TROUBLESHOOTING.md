# Troubleshooting

## `poetry` is not recognized
Install Poetry using the official Poetry installer or `pipx install poetry`, then open a new terminal and run `poetry --version`.

## Poetry selects the wrong Python

```powershell
poetry env remove --all
poetry env use 3.12
poetry run python --version
```

Expected: Python 3.12.x.

## `az` is not recognized
You do not need Azure CLI for the Python POC. Set `AZURE_AUTH_MODE=browser`. If you want Terraform/CLI authentication, install Azure CLI and restart your terminal so PATH is refreshed.

## 403 from ADLS
Confirm Storage Blob Data Contributor is assigned at the storage account/container scope and sign in again. RBAC propagation can take a few minutes.

## Event Hubs CBS / authorization failure
Confirm `EVENTHUB_NAME` is the hub name, not the namespace. For RBAC, assign Data Sender/Receiver. For connection-string mode, use a policy that has the required Send/Listen right.

## Search vector dimension error
The search index vector field dimension must match the embedding model output. Set `SEARCH_VECTOR_DIMENSIONS` correctly, delete/recreate the index if necessary, then re-index.

## Search 403
For key mode, use admin key to create/load the index and query key for query-only operations. For RBAC, check Search Service Contributor / Search Index Data Contributor / Search Index Data Reader roles as applicable.

## Foundry `AttributeError` / endpoint problem
This project targets the new Foundry SDK (`azure-ai-projects>=2.0`). Confirm the endpoint looks like:

`https://<resource>.services.ai.azure.com/api/projects/<project>`

Then run `poetry show azure-ai-projects` and verify you did not accidentally install a classic 1.x environment.

## Document Intelligence `InvalidContent`
Confirm the file exists and is a supported PDF/image, then rerun with `data/synthetic/invoice_001.pdf`. If a custom scan fails, open it locally to verify it is not corrupt.
