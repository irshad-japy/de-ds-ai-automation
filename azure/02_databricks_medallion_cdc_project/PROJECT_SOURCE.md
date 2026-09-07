# Project source

This runnable project is based on the supplied `POC_02_DATABRICKS_MEDALLION_CDC.md` specification and the later `step_terraform.md` manual setup notes.

The Terraform update preserves the same POC goals while moving disposable infrastructure/governance/workspace provisioning to Terraform and Windows CMD wrappers. The PySpark notebooks remain the execution layer for Bronze/Silver/Gold, Auto Loader, quality/quarantine, MERGE, SCD1/SCD2, schema evolution, and CDF.
