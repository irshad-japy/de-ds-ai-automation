output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "storage_account_name" {
  value = azurerm_storage_account.this.name
}

output "storage_dfs_url" {
  value = azurerm_storage_account.this.primary_dfs_endpoint
}

output "data_factory_name" {
  value = azurerm_data_factory.this.name
}

output "data_factory_managed_identity_object_id" {
  value = azurerm_data_factory.this.identity[0].principal_id
}

output "sql_server_fqdn" {
  value = azurerm_mssql_server.this.fully_qualified_domain_name
}

output "sql_database_name" {
  value = azurerm_mssql_database.this.name
}

output "key_vault_uri" {
  value = azurerm_key_vault.this.vault_uri
}
