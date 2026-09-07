terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.2"
    }

    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.128"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }

    time = {
      source  = "hashicorp/time"
      version = "~> 0.13"
    }
  }
}
