variable "subscription_id" {
  description = "Azure subscription ID selected with az login / az account set."
  type        = string

  validation {
    condition     = length(trimspace(var.subscription_id)) > 0
    error_message = "subscription_id must not be empty. Run cmd\\01_configure_terraform.cmd or edit terraform.tfvars."
  }
}

variable "location" {
  description = "Azure region. Keep all POC resources in the same region."
  type        = string
  default     = "centralindia"
}

variable "resource_group_name" {
  type    = string
  default = "rg-azde-poc02"
}

variable "storage_account_prefix" {
  description = "Lowercase alphanumeric prefix; Terraform adds a random suffix for global uniqueness."
  type        = string
  default     = "stazdepoc02"
}

variable "container_name" {
  type    = string
  default = "poc02"
}

variable "access_connector_name" {
  type    = string
  default = "ac-azde-poc02"
}

variable "databricks_workspace_name" {
  type    = string
  default = "dbw-azde-poc02"
}

variable "databricks_workspace_sku" {
  description = "Premium is used because this POC exercises Unity Catalog governance."
  type        = string
  default     = "premium"
}

variable "storage_credential_name" {
  type    = string
  default = "poc02_storage_cred"
}

variable "external_location_name" {
  type    = string
  default = "poc02_ext"
}

variable "catalog_name" {
  type    = string
  default = "azde_poc"
}

variable "workspace_project_folder" {
  type    = string
  default = "/Shared/POC_02_DATABRICKS_MEDALLION_CDC"
}

variable "job_num_workers" {
  description = "Small POC job compute. One worker means driver + one worker and avoids region-specific single-node restrictions."
  type        = number
  default     = 1
}

variable "tags" {
  type = map(string)
  default = {
    project     = "POC-02-Databricks-Medallion-CDC"
    environment = "lab"
    managed_by  = "terraform"
  }
}
