# Troubleshooting

## 1. `az` is not recognized

Azure CLI is not installed or not on PATH. Install Azure CLI, close/reopen Command Prompt or PowerShell, then run:

```powershell
az version
az login
```

## 2. `DefaultAzureCredential failed`

For local work:

```powershell
az login
az account show
```

For Blob Storage, your user needs data-plane RBAC such as `Storage Blob Data Contributor`.

For Document Intelligence with Entra ID, your identity needs `Cognitive Services User`. A single-service Document Intelligence resource/custom subdomain is required for Entra authentication. For a first local run, you may instead place the Document Intelligence key in your local `.env` file only.

## 3. Storage `AuthorizationPermissionMismatch`

Assign your signed-in identity the `Storage Blob Data Contributor` role on the storage account and wait a few minutes for RBAC propagation.

## 4. Document Intelligence `401` / `403`

Check endpoint and credentials. If using Entra ID, confirm the `Cognitive Services User` role. If using key auth, confirm `DOCUMENTINTELLIGENCE_API_KEY` is loaded from `.env` and has no quotes/spaces.

## 5. Document Intelligence `InvalidContent`

Make sure the input is a supported PDF/image and not empty/corrupted. The included samples are normal text PDFs.

## 6. SQL login/authentication errors

Run `az login`, verify your Azure SQL server has a Microsoft Entra administrator, and ensure your public client IP is allowed during local testing. The recommended local connection string uses `Authentication=ActiveDirectoryDefault`.

## 7. `mssql-python` installation problem

Microsoft notes that Linux/macOS may require system dependencies. Windows is the simplest local path for this POC. If Function deployment fails because of native driver dependencies, first complete the local batch POC; then use a custom Linux container or switch the SQL loading layer to a driver supported by your Function runtime.

## 8. Malformed invoice did not fail

AI extraction can interpret a visually malformed document differently from expectation. Inspect the generated normalized JSON and raw result. You can force the test by temporarily increasing `CRITICAL_CONFIDENCE_THRESHOLD` (for example 0.99), or edit the malformed sample to remove its invoice number / make totals inconsistent.

## 9. Function triggers repeatedly

The Function only triggers on `documents/incoming/{name}`. Outputs are written under `processed/` and `failed/`, so they should not retrigger the function. The SHA-256 marker provides idempotency if the same input is seen again.
