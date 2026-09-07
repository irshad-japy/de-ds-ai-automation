# Terraform folder

This folder provisions the disposable Azure + Azure Databricks infrastructure for POC-02.

Run the Windows scripts from `../cmd/` in numeric order, or use the exact Terraform commands documented in the project root `README.md`.

Terraform owns:

- Resource group
- ADLS Gen2 storage account and `poc02` container
- logical ADLS folder markers
- Azure Databricks Access Connector with system-assigned managed identity
- Azure RBAC for the Access Connector and the logged-in user
- Azure Databricks Premium workspace
- Unity Catalog storage credential and external location
- `azde_poc` catalog + Bronze/Silver/Gold/Quarantine schemas
- Databricks notebook imports
- Phase-1 and Phase-2 Databricks Jobs

The notebooks create the Delta tables/data so the actual CDC/SCD exercise remains visible and educational. `terraform destroy` deletes the Terraform-managed catalog with `force_destroy=true`, then the Databricks objects and Azure resources.
