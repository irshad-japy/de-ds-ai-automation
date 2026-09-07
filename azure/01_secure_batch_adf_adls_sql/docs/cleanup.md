# Cleanup — stop POC costs

This POC is intentionally isolated in:

```text
rg-azde-poc01-dev
```

## Before cleanup

Capture only sanitized evidence:

- architecture screenshot/diagram,
- ADF pipeline canvas with no secrets,
- successful Monitor run,
- SQL verification counts,
- archive/quarantine container paths,
- controlled failure evidence,
- sanitized Terraform plan/output if useful.

## Azure CLI cleanup

First inspect:

```powershell
az group show -n rg-azde-poc01-dev -o table
az resource list -g rg-azde-poc01-dev -o table
```

Then delete only when you are sure:

```powershell
az group delete -n rg-azde-poc01-dev --yes
```

Or use the repository guardrail script:

```powershell
.\scripts\cleanup_resource_group.ps1 -ResourceGroup rg-azde-poc01-dev -ConfirmDelete
```

## Terraform cleanup

If Terraform created the resources and your state is intact:

```powershell
cd infra/terraform
terraform plan -destroy
terraform destroy
```

Review before confirmation.

## After cleanup

Verify the Resource Group no longer appears under your subscription resources. Also verify no separately-created resource was accidentally placed outside the Resource Group.
