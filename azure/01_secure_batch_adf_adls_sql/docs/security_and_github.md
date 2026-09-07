# Security and GitHub hygiene

## What this POC is trying to demonstrate

The security objective is not only "use Azure". It is to practice a credential-minimized design:

- ADF uses system-assigned Managed Identity.
- ADLS access uses Azure RBAC/Entra.
- Azure SQL recognizes the ADF identity as a contained database user.
- Local Python uses `DefaultAzureCredential` after `az login`.
- Key Vault is available for connectors that genuinely need a secret.
- Exported JSON is sanitized.

## Never commit these

```text
.env
terraform.tfvars
*.tfstate
*.tfstate.*
Storage account keys
SAS URLs/tokens
SQL admin password
service principal client secret
private keys / certificates
real bearer tokens
connection strings containing credentials
```

## Safe placeholders

Use patterns like:

```text
<STORAGE_ACCOUNT>
<SQL_SERVER>
<ADF_NAME>
<YOUR_SUBSCRIPTION_ID>
```

## Before `git add .`

Run:

```powershell
git status
```

Then search common secret words:

```powershell
Get-ChildItem -Recurse -File | Select-String -Pattern "AccountKey=|SharedAccessSignature=|client_secret|password=|sig="
```

Review every hit manually. False positives are possible.

## ADF Git integration caution

ADF publishes JSON artifacts. Managed Identity-based linked-service JSON is much safer than embedding keys, but always inspect exported artifacts before public GitHub commits.

Do not publish:

- private endpoint DNS/IP details that you consider sensitive,
- real secret names if they reveal confidential systems,
- screenshots that contain email addresses, subscription IDs, tenant IDs, tokens, or private URLs.

## Key Vault principle

Key Vault is for secrets, keys, and certificates when they are actually needed. It is not better to replace a Managed Identity connection with a password merely so Key Vault appears in the architecture.

Managed Identity removes secret rotation/handling from the application path. Prefer it when the target service supports it.

## RBAC principle

Assign the narrowest role at the narrowest practical scope.

This POC uses `Storage Blob Data Contributor` because ADF needs to:

- read landing,
- write archive,
- write quarantine,
- delete successfully archived landing files.

An enterprise design may split identities or use per-container ACL/RBAC to tighten this further.
