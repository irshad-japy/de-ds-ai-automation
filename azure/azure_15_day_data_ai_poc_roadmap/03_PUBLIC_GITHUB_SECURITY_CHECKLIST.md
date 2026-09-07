# Public GitHub Security Checklist

Run this checklist before every push.

## Never commit

- Azure Storage account keys
- SAS tokens or SAS URLs
- Azure SQL passwords
- service principal client secrets
- Foundry/OpenAI keys
- Azure AI Search admin/query keys
- Document Intelligence keys
- Key Vault secret values
- `.env`
- `terraform.tfstate`
- `terraform.tfstate.backup`
- local `*.tfvars` containing real IDs/secrets
- downloaded publish profiles
- certificates/private keys
- portal screenshots showing secrets
- real customer/company datasets
- personal documents, invoices or email content

## Safe patterns

- `.env.example` contains placeholders only.
- Use `DefaultAzureCredential` locally.
- Use Managed Identity in Azure.
- Use Key Vault references where a secret is unavoidable.
- Grant least-privilege RBAC.
- Give an agent read-only data access.
- Use synthetic data.
- Use one resource group per POC.
- Put deployment-specific values in environment variables.
- Parameterize IaC.
- Keep private networking as an optional advanced lab if it would materially increase cost.

## Recommended `.gitignore`

```gitignore
.env
.env.*
!.env.example
*.pem
*.pfx
*.key
*.cer
*.publishsettings
terraform.tfstate
terraform.tfstate.*
*.tfvars
.terraform/
__pycache__/
.venv/
.vscode/settings.json
evidence/private/
local_config/
```

## Before push

```bash
git status
git diff --cached
git grep -n -I -E "(AccountKey=|SharedAccessSignature=|client_secret|api[_-]?key|password\s*=|sig=)"
```

Also use a secret-scanning tool such as Gitleaks or GitHub secret scanning.

## If a secret is accidentally committed

1. Revoke/rotate it immediately in Azure.
2. Remove it from the Git history.
3. Verify the old credential no longer works.
4. Inspect Azure activity logs for unexpected use.
5. Never rely only on deleting the latest commit.
