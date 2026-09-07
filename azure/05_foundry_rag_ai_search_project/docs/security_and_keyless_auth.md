# Security and Keyless Authentication

## Beginner path

First get the POC working with local keys in `.env`.

This is acceptable for a personal learning POC only if:

- `.env` is in `.gitignore`;
- you never paste keys into screenshots, Markdown, issue tickets, or commits;
- you rotate a key immediately if it is accidentally exposed.

## Recommended next step: Microsoft Entra ID

### Azure AI Search

1. Open the Search service.
2. Go to **Settings → Keys**.
3. Keep `Both` authentication modes temporarily while configuring RBAC.
4. Open **Access control (IAM)**.
5. Assign your user the roles needed for this POC:
   - Search Service Contributor
   - Search Index Data Contributor
   - Search Index Data Reader
6. Run `az login` locally.
7. Change `.env`:

```dotenv
SEARCH_AUTH_MODE=entra
AZURE_SEARCH_ADMIN_KEY=
```

8. Re-run retrieval/ingestion.
9. After you prove RBAC works, you can choose role-based access only if that fits your setup.

### Microsoft Foundry

1. Assign your user the model-inference role required by your Foundry resource/deployment path (commonly Azure AI User for Foundry model access).
2. Run:

```powershell
az login
```

3. Change:

```dotenv
FOUNDRY_AUTH_MODE=entra
FOUNDRY_API_KEY=
```

The code uses `DefaultAzureCredential`, so local Azure CLI credentials can be used. In Azure hosting, the same pattern can resolve a managed identity.

## Managed Identity hosting pattern

When you later deploy FastAPI to Azure Functions, App Service, or Container Apps:

1. enable the workload's system-assigned managed identity;
2. assign only the required Search and Foundry roles to that identity;
3. use `SEARCH_AUTH_MODE=entra` and `FOUNDRY_AUTH_MODE=entra`;
4. do not copy local Azure CLI credentials into Azure;
5. use Key Vault only for secrets that still cannot be removed.

## Key Vault

Key Vault is optional in this local POC because Entra ID can remove most key usage. If another secret remains, store it in Key Vault and grant the workload identity `Key Vault Secrets User` instead of putting the secret directly in application settings.
