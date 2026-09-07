provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# The Databricks provider reuses the Azure CLI login from `az login`.
# workspace_url is created by AzureRM during this same Terraform deployment.
provider "databricks" {
  host                        = azurerm_databricks_workspace.poc02.workspace_url
  azure_workspace_resource_id = azurerm_databricks_workspace.poc02.id
}
