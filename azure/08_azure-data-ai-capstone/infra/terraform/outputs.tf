output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "adls_account_name" {
  value = azurerm_storage_account.adls.name
}

output "adls_account_url" {
  value = azurerm_storage_account.adls.primary_dfs_endpoint
}

output "eventhub_namespace" {
  value = try(azurerm_eventhub_namespace.events[0].name, null)
}

output "eventhub_fqdn" {
  value = try("${azurerm_eventhub_namespace.events[0].name}.servicebus.windows.net", null)
}

output "search_service_name" {
  value = try(azurerm_search_service.search[0].name, null)
}

output "search_endpoint" {
  value = try("https://${azurerm_search_service.search[0].name}.search.windows.net", null)
}

output "key_vault_name" {
  value = azurerm_key_vault.kv.name
}
