# Bicep alternative

The capstone primarily uses Terraform, but this small Bicep file is included so CI can demonstrate Bicep syntax validation too.

```powershell
az bicep build --file infra/bicep/main.bicep
```

To deploy it, first create/select a resource group and provide globally unique `storageName`.
