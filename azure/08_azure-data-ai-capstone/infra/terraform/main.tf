resource "random_string" "suffix" {
  length  = 5
  upper   = false
  special = false
}

locals {
  compact = lower(replace(var.project_name, "-", ""))
  suffix  = random_string.suffix.result
  tags = {
    project = "POC-08"
    env     = "lab"
  }
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.tags
}

resource "azurerm_storage_account" "adls" {
  name                     = substr("${local.compact}${local.suffix}", 0, 24)
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "datalake" {
  name               = "datalake"
  storage_account_id = azurerm_storage_account.adls.id
}

resource "azurerm_log_analytics_workspace" "logs" {
  name                = "log-${var.project_name}-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

resource "azurerm_application_insights" "appi" {
  name                = "appi-${var.project_name}-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  workspace_id        = azurerm_log_analytics_workspace.logs.id
  application_type    = "web"
  tags                = local.tags
}

resource "azurerm_key_vault" "kv" {
  name                      = substr("kv-${var.project_name}-${local.suffix}", 0, 24)
  location                  = azurerm_resource_group.this.location
  resource_group_name       = azurerm_resource_group.this.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  purge_protection_enabled  = false
  soft_delete_retention_days = 7
  tags                      = local.tags
}

resource "azurerm_eventhub_namespace" "events" {
  count               = var.deploy_eventhub ? 1 : 0
  name                = "evhns-${var.project_name}-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "Standard"
  capacity            = 1
  tags                = local.tags
}

resource "azurerm_eventhub" "shipments" {
  count               = var.deploy_eventhub ? 1 : 0
  name                = "shipment-events"
  namespace_id        = azurerm_eventhub_namespace.events[0].id
  partition_count     = 2
  message_retention   = 1
}

resource "azurerm_search_service" "search" {
  count               = var.deploy_search ? 1 : 0
  name                = "srch-${var.project_name}-${local.suffix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = var.search_sku
  tags                = local.tags
}

resource "azurerm_databricks_workspace" "dbw" {
  count                       = var.deploy_databricks ? 1 : 0
  name                        = "dbw-${var.project_name}-${local.suffix}"
  resource_group_name         = azurerm_resource_group.this.name
  location                    = azurerm_resource_group.this.location
  sku                         = "standard"
  managed_resource_group_name = "rg-managed-dbw-${var.project_name}-${local.suffix}"
  tags                        = local.tags
}
