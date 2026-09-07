output "resource_group_name" {
  value = azurerm_resource_group.poc02.name
}

output "location" {
  value = azurerm_resource_group.poc02.location
}

output "storage_account_name" {
  value = azurerm_storage_account.adls.name
}

output "container_name" {
  value = azurerm_storage_container.poc02.name
}

output "abfss_root" {
  value = local.abfss_root
}

output "access_connector_resource_id" {
  value = azurerm_databricks_access_connector.poc02.id
}

output "databricks_workspace_url" {
  value = "https://${azurerm_databricks_workspace.poc02.workspace_url}/"
}

output "unity_catalog_metastore_id" {
  value = data.databricks_current_metastore.this.id
}

output "storage_credential_name" {
  value = databricks_storage_credential.poc02.name
}

output "external_location_name" {
  value = databricks_external_location.poc02.name
}

output "catalog_name" {
  value = databricks_catalog.poc02.name
}

output "phase1_job_id" {
  value = databricks_job.phase1.id
}

output "phase1_job_url" {
  value = databricks_job.phase1.url
}

output "phase2_job_id" {
  value = databricks_job.phase2.id
}

output "phase2_job_url" {
  value = databricks_job.phase2.url
}

output "important_next_steps" {
  value = <<-EOT
    1. Run ..\\cmd\\03_upload_phase1.cmd
    2. Open phase1_job_url and Run now
    3. Run validation SQL
    4. Run ..\\cmd\\05_upload_phase2.cmd
    5. Open phase2_job_url and Run now (rerun once if Auto Loader reports the expected schema-evolution restart)
    6. Validate SCD2 + CDF
    7. Run ..\\cmd\\07_destroy.cmd
  EOT
}
