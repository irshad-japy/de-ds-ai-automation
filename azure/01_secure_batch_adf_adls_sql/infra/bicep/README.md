# Bicep comparison mini-lab

This file only recreates the Storage/ADLS portion so you can compare Bicep syntax with Terraform.

From the project root:

```powershell
az bicep version
az deployment group what-if `
  --resource-group rg-azde-poc01-dev `
  --template-file infra/bicep/storage_only.bicep `
  --parameters storageAccountName=<UNIQUE_STORAGE_NAME>
```

Use `what-if` first. Deploy only if you intentionally want a second storage resource or if you are rebuilding after cleanup.
