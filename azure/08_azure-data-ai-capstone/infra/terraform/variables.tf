variable "subscription_id" {
  type        = string
  description = "Azure subscription id"
}

variable "location" {
  type    = string
  default = "eastus"
}

variable "resource_group_name" {
  type    = string
  default = "rg-poc08-capstone"
}

variable "project_name" {
  type    = string
  default = "poc08capstone"
}

variable "search_sku" {
  type        = string
  default     = "free"
  description = "Use basic if your subscription already has a free Search service or the region does not allow free."
}

variable "deploy_eventhub" {
  type    = bool
  default = true
}

variable "deploy_search" {
  type    = bool
  default = true
}

variable "deploy_databricks" {
  type        = bool
  default     = false
  description = "Keep false if reusing POC-02 Databricks. Enabling can incur cost."
}
