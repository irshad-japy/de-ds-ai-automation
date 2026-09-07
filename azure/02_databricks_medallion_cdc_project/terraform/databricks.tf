# New Azure Databricks workspaces are normally Unity Catalog enabled automatically.
# This data source is also an early verification that a metastore is attached.
data "databricks_current_metastore" "this" {
  depends_on = [azurerm_databricks_workspace.poc02]
}

data "databricks_current_user" "me" {
  depends_on = [azurerm_databricks_workspace.poc02]
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
  depends_on        = [azurerm_databricks_workspace.poc02]
}

data "databricks_node_type" "smallest" {
  local_disk = true
  depends_on = [azurerm_databricks_workspace.poc02]
}

resource "databricks_storage_credential" "poc02" {
  name = var.storage_credential_name

  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.poc02.id
  }

  comment = "POC-02 managed identity storage credential - managed by Terraform"

  lifecycle {
    precondition {
      condition     = data.databricks_current_metastore.this.id != "no_metastore"
      error_message = "This workspace has no Unity Catalog metastore assigned. Attach/enable Unity Catalog, then rerun terraform apply."
    }
  }

  depends_on = [time_sleep.after_rbac]
}

resource "databricks_external_location" "poc02" {
  name            = var.external_location_name
  url             = local.abfss_root
  credential_name = databricks_storage_credential.poc02.id
  comment         = "POC-02 ADLS Gen2 external location - managed by Terraform"
  force_destroy   = true

  depends_on = [time_sleep.after_rbac]
}

# Explicitly demonstrate UC privileges required by this POC.
resource "databricks_grants" "external_location_current_user" {
  external_location = databricks_external_location.poc02.id

  grant {
    principal = data.databricks_current_user.me.user_name
    privileges = [
      "CREATE_EXTERNAL_TABLE",
      "CREATE_MANAGED_STORAGE",
      "READ_FILES",
      "WRITE_FILES"
    ]
  }
}

resource "databricks_catalog" "poc02" {
  name          = var.catalog_name
  storage_root  = "${local.abfss_root}/managed/${var.catalog_name}"
  comment       = "POC-02 Medallion catalog managed by Terraform"
  force_destroy = true

  properties = {
    purpose    = "databricks-medallion-cdc-poc"
    managed_by = "terraform"
  }

  depends_on = [
    databricks_external_location.poc02,
    databricks_grants.external_location_current_user
  ]
}

resource "databricks_schema" "bronze" {
  catalog_name  = databricks_catalog.poc02.name
  name          = "bronze"
  comment       = "Raw incremental ingestion plus audit metadata"
  force_destroy = true
}

resource "databricks_schema" "silver" {
  catalog_name  = databricks_catalog.poc02.name
  name          = "silver"
  comment       = "Validated, standardized and deduplicated records"
  force_destroy = true
}

resource "databricks_schema" "gold" {
  catalog_name  = databricks_catalog.poc02.name
  name          = "gold"
  comment       = "Business-ready facts, dimensions and CDF audit"
  force_destroy = true
}

resource "databricks_schema" "quarantine" {
  catalog_name  = databricks_catalog.poc02.name
  name          = "quarantine"
  comment       = "Invalid records and data quality failure reasons"
  force_destroy = true
}

resource "databricks_directory" "project" {
  path = var.workspace_project_folder
}

locals {
  notebooks = {
    "00_setup"                  = "00_setup.py"
    "01_bronze_ingest"          = "01_bronze_ingest.py"
    "02_silver_quality"         = "02_silver_quality.py"
    "03_gold_dimensions"        = "03_gold_dimensions.py"
    "04_cdf_consumer"           = "04_cdf_consumer.py"
    "05_performance_governance" = "05_performance_governance.py"
  }
}

resource "databricks_notebook" "poc02" {
  for_each = local.notebooks

  source   = "${path.module}/../notebooks/${each.value}"
  path     = "${databricks_directory.project.path}/${each.key}"
  language = "PYTHON"
}

# Phase-1 job: initial Bronze -> Silver -> Gold build.
resource "databricks_job" "phase1" {
  name        = "POC02-Phase1-Medallion"
  description = "Initial POC-02 load. Upload Phase-1 CSV files before running."

  job_cluster {
    job_cluster_key = "poc02_small_cluster"
    new_cluster {
      spark_version      = data.databricks_spark_version.latest_lts.id
      node_type_id       = data.databricks_node_type.smallest.id
      num_workers        = 0
      data_security_mode = "SINGLE_USER"

      spark_conf = {
        "spark.master"                     = "local[*]"
        "spark.databricks.cluster.profile" = "singleNode"
      }

      custom_tags = {
        "ResourceClass" = "SingleNode"
      }
    }
  }

  task {
    task_key        = "setup"
    job_cluster_key = "poc02_small_cluster"

    notebook_task {
      notebook_path = databricks_notebook.poc02["00_setup"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
      }
    }
  }

  task {
    task_key        = "bronze"
    job_cluster_key = "poc02_small_cluster"

    depends_on {
      task_key = "setup"
    }

    notebook_task {
      notebook_path = databricks_notebook.poc02["01_bronze_ingest"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
        batch_id        = "phase1"
      }
    }
  }

  task {
    task_key        = "silver"
    job_cluster_key = "poc02_small_cluster"

    depends_on {
      task_key = "bronze"
    }

    notebook_task {
      notebook_path = databricks_notebook.poc02["02_silver_quality"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
      }
    }
  }

  task {
    task_key        = "gold"
    job_cluster_key = "poc02_small_cluster"

    depends_on {
      task_key = "silver"
    }

    notebook_task {
      notebook_path = databricks_notebook.poc02["03_gold_dimensions"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
      }
    }
  }

  depends_on = [
    databricks_schema.bronze,
    databricks_schema.silver,
    databricks_schema.gold,
    databricks_schema.quarantine
  ]
}

# Phase-2 job: incremental files -> schema evolution -> MERGE/SCD -> CDF consumer.
resource "databricks_job" "phase2" {
  name        = "POC02-Phase2-Incremental-CDC"
  description = "Run after Phase-2 CSV upload. Rerun if Auto Loader first stops after discovering the new column."

  job_cluster {
    job_cluster_key = "poc02_small_cluster"

    new_cluster {
      spark_version      = data.databricks_spark_version.latest_lts.id
      node_type_id       = data.databricks_node_type.smallest.id
      num_workers        = 0
      data_security_mode = "SINGLE_USER"

      spark_conf = {
        "spark.master"                     = "local[*]"
        "spark.databricks.cluster.profile" = "singleNode"
      }

      custom_tags = {
        "ResourceClass" = "SingleNode"
      }
    }
  }

  task {
    task_key        = "bronze_incremental"
    job_cluster_key = "poc02_small_cluster"

    notebook_task {
      notebook_path = databricks_notebook.poc02["01_bronze_ingest"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
        batch_id        = "phase2"
      }
    }
  }

  task {
    task_key        = "silver_refresh"
    job_cluster_key = "poc02_small_cluster"

    depends_on {
      task_key = "bronze_incremental"
    }

    notebook_task {
      notebook_path = databricks_notebook.poc02["02_silver_quality"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
      }
    }
  }

  task {
    task_key        = "gold_merge_scd"
    job_cluster_key = "poc02_small_cluster"

    depends_on {
      task_key = "silver_refresh"
    }

    notebook_task {
      notebook_path = databricks_notebook.poc02["03_gold_dimensions"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
      }
    }
  }

  task {
    task_key        = "cdf_consumer"
    job_cluster_key = "poc02_small_cluster"

    depends_on {
      task_key = "gold_merge_scd"
    }

    notebook_task {
      notebook_path = databricks_notebook.poc02["04_cdf_consumer"].path
      base_parameters = {
        storage_account = local.storage_account_name
        container       = var.container_name
        catalog         = var.catalog_name
      }
    }
  }

  depends_on = [databricks_job.phase1]
}