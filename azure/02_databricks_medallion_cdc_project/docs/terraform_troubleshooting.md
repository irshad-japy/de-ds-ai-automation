# Terraform / CMD troubleshooting — POC-02

## `az` is not recognized

`azure-identity` is a Python SDK and does not install Azure CLI. Install Azure CLI, close/reopen Command Prompt, then verify:

```cmd
az --version
az login
```

## `terraform` is not recognized

Install Terraform CLI and ensure the folder containing `terraform.exe` is in Windows PATH. Reopen CMD:

```cmd
terraform version
```

## AzureRM says subscription ID is required

Run:

```cmd
cmd\01_configure_terraform.cmd
```

This writes the selected subscription ID to `terraform\terraform.tfvars` and runs `az account set`.

## `AuthorizationFailed` while creating `azurerm_role_assignment`

The identity running Terraform must be allowed to create Azure role assignments. For a personal lab this normally means an Azure role such as Owner or User Access Administrator at the required scope.

Do not bypass this by hard-coding a storage key into notebooks.

## Databricks provider cannot authenticate to new workspace

Verify:

```cmd
az account show --output table
cd terraform
terraform output databricks_workspace_url
```

Keep the Terraform state and rerun `cmd\02_terraform_apply.cmd`. Terraform will not intentionally duplicate resources already tracked in state.

## `no_metastore` / Unity Catalog is not attached

The Terraform config deliberately checks the workspace's current metastore before creating Unity Catalog storage objects. New workspaces are normally automatically Unity Catalog enabled, but if the account/workspace does not have a metastore assignment, attach/enable Unity Catalog first and rerun `terraform apply`.

## External location validation / permission denied

Confirm Terraform created both RBAC assignments:

```cmd
cd terraform
terraform state show azurerm_role_assignment.access_connector_storage
terraform state show azurerm_role_assignment.current_user_storage
```

Then rerun apply. Do not replace the managed identity with secrets for this POC.

## ADLS upload returns AuthorizationPermissionMismatch

Confirm you are logged in with the same identity used by Terraform:

```cmd
az account show --output table
```

Then inspect the current-user role assignment in Terraform state and rerun the upload script.

## Job compute cannot be created / quota error

The Terraform job uses the provider's smallest available node type and one worker. If the selected VM family is unavailable due to subscription quota or regional capacity, inspect available Databricks node types and adjust the compute configuration. Keep the job ephemeral and small.

## Phase-2 job stops in Bronze after discovering `sales_channel`

This is expected for the schema evolution exercise with Auto Loader `addNewColumns`. Run Phase 2 again after the schema metadata has been updated.

## `terraform destroy` is blocked by non-empty catalog

The Terraform-managed `azde_poc` catalog sets `force_destroy = true`. First rerun:

```cmd
cd terraform
terraform plan -destroy
```

Inspect which Databricks object is blocking deletion. Avoid deleting random resources manually, because that creates Terraform state drift.

## Terraform state was deleted accidentally

Do not run a blind resource-group deletion as your first fix. Without state, Terraform no longer knows which resources it owns. For a disposable personal lab, you can inspect the dedicated POC resource group carefully and clean it up, but for reusable environments you should recover/import state instead.
