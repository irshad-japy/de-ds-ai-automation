variable "subscription_id" {
  description = "Azure subscription ID. Prefer ARM_SUBSCRIPTION_ID environment variable when possible."
  type        = string
  default     = null
}

variable "location" {
  description = "Azure region for POC resources."
  type        = string
  default     = "centralindia"
}

variable "resource_group_name" {
  type    = string
  default = "rg-azde-poc01-dev"
}

variable "storage_account_name" {
  description = "Globally unique, lowercase letters/numbers only."
  type        = string
}

variable "data_factory_name" {
  description = "Globally unique Data Factory name."
  type        = string
}

variable "sql_server_name" {
  description = "Globally unique Azure SQL logical server name (without .database.windows.net)."
  type        = string
}

variable "sql_database_name" {
  type    = string
  default = "sqldb-azde-poc01-dev"
}

variable "sql_admin_login" {
  description = "Bootstrap SQL admin login. Do not commit the real value."
  type        = string
  sensitive   = true
}

variable "sql_admin_password" {
  description = "Bootstrap SQL admin password. Do not commit the real value."
  type        = string
  sensitive   = true
}

variable "key_vault_name" {
  description = "Globally unique Key Vault name."
  type        = string
}

variable "client_ip" {
  description = "Optional public IPv4 address of your laptop for SQL admin bootstrap access."
  type        = string
  default     = null
}

variable "uploader_object_id" {
  description = "Optional Microsoft Entra object ID of your developer user. If set, grants Storage Blob Data Contributor for Python upload."
  type        = string
  default     = null
}

variable "create_log_analytics" {
  description = "Create a small Log Analytics workspace for optional diagnostics practice."
  type        = bool
  default     = false
}

variable "tags" {
  type = map(string)
  default = {
    project     = "azure-poc"
    environment = "dev"
    owner       = "personal"
    autoDelete  = "true"
  }
}
