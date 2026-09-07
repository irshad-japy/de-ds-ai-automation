data "azurerm_client_config" "current" {}

resource "random_string" "storage_suffix" {
  length  = 6
  upper   = false
  special = false
  numeric = true
}

locals {
  storage_account_name = lower("${var.storage_account_prefix}${random_string.storage_suffix.result}")
  abfss_root           = "abfss://${var.container_name}@${local.storage_account_name}.dfs.core.windows.net"

  folder_markers = toset([
    "raw/orders/.keep",
    "raw/customers/.keep",
    "checkpoints/.keep",
    "schema/.keep",
    "quarantine/.keep",
    "managed/.keep"
  ])
}

resource "azurerm_resource_group" "poc02" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_storage_account" "adls" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.poc02.name
  location                 = azurerm_resource_group.poc02.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true
  min_tls_version          = "TLS1_2"

  # Kept enabled for a beginner POC and Terraform storage data-plane operations.
  # Do not expose account keys in Git or outputs.
  shared_access_key_enabled = true

  tags = var.tags
}

resource "azurerm_storage_container" "poc02" {
  name                  = var.container_name
  storage_account_id    = azurerm_storage_account.adls.id
  container_access_type = "private"
}

# These zero-byte markers make the desired logical ADLS directory structure
# visible immediately. Auto Loader writes its own checkpoint/schema data later.
resource "azurerm_storage_blob" "folder_markers" {
  for_each = local.folder_markers

  name                 = each.value
  storage_container_id = azurerm_storage_container.poc02.id
  type                 = "Block"
  source_content       = ""
}

resource "azurerm_databricks_access_connector" "poc02" {
  name                = var.access_connector_name
  resource_group_name = azurerm_resource_group.poc02.name
  location            = azurerm_resource_group.poc02.location

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Databricks managed identity -> ADLS data access.
resource "azurerm_role_assignment" "access_connector_storage" {
  scope                            = azurerm_storage_account.adls.id
  role_definition_name             = "Storage Blob Data Contributor"
  principal_id                     = azurerm_databricks_access_connector.poc02.identity[0].principal_id
  principal_type                   = "ServicePrincipal"
  skip_service_principal_aad_check = true
}

# Your current az-login identity -> ADLS data access so the CMD upload scripts can
# use --auth-mode login instead of putting storage keys in scripts.
resource "azurerm_role_assignment" "current_user_storage" {
  scope                = azurerm_storage_account.adls.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_databricks_workspace" "poc02" {
  name                        = var.databricks_workspace_name
  resource_group_name         = azurerm_resource_group.poc02.name
  location                    = azurerm_resource_group.poc02.location
  sku                         = var.databricks_workspace_sku
  managed_resource_group_name = "${var.resource_group_name}-databricks-managed"

  tags = var.tags
}

# Azure RBAC can be eventually consistent. This short dependency gives the
# workspace-side external-location validation a better chance to succeed on the
# same `terraform apply`. If Azure still reports permission propagation, rerun apply.
resource "time_sleep" "after_rbac" {
  create_duration = "45s"

  depends_on = [
    azurerm_role_assignment.access_connector_storage,
    azurerm_role_assignment.current_user_storage
  ]
}
