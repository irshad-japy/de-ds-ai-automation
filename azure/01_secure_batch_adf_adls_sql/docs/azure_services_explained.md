# Azure services explained simply — POC-01

## Resource Group

Think of it as the project folder for Azure resources. Putting this POC in one Resource Group makes ownership, tags, cost review, and deletion easier.

## Cost Management Budget

A budget is an alerting/awareness mechanism. It warns you when spend approaches thresholds; it is not automatically a hard shutdown switch.

## ADLS Gen2

Azure Data Lake Storage Gen2 is built on Azure Storage with hierarchical namespace capabilities. In this POC it is the durable file zone.

- `landing` = newly arrived files waiting for processing
- `archive` = successfully processed raw files kept for audit/replay
- `quarantine` = incompatible/error evidence that needs investigation

## Azure Data Factory (ADF)

ADF is the orchestration and data-movement service. It coordinates steps rather than being the final storage system.

In this POC ADF asks:

1. Does the file exist?
2. Was it already processed?
3. Can I copy compatible rows to staging?
4. Can SQL validate/merge them?
5. If successful, can I archive the raw file?

## Linked Service

A linked service is roughly ADF's connection definition for a system such as ADLS or Azure SQL. Authentication belongs here, but this POC uses Managed Identity so no password needs to be committed.

## Dataset

A dataset describes the shape/location of data used by an activity. Here datasets are parameterized so one definition can point to different containers, folders, files, or SQL tables.

## Integration Runtime

The Integration Runtime is the compute/connectivity layer ADF uses to move data and connect to systems.

- Azure Integration Runtime: cloud-hosted, used by the main POC.
- Self-hosted Integration Runtime: optional, used when ADF must reach local/on-premises/private systems through a machine you manage.

## Azure SQL Database

Azure SQL stores the relational staging/control/curated data.

- `orders_stg` = temporary typed ingestion area
- `orders` = curated final business table
- `orders_rejects` = business-rule failures
- `etl_file_log` = processed-file control/idempotency
- `etl_watermark` = last successful pipeline progress

## Microsoft Entra ID

Entra ID is Azure's identity system. Users, groups, applications, and managed identities can authenticate through Entra.

## Managed Identity

ADF gets its own Azure-managed identity. Azure manages the credentials behind it, so you do not copy a client secret into code.

## Azure RBAC

RBAC answers: **What Azure actions may this identity perform, and at what scope?**

ADF gets `Storage Blob Data Contributor` because it needs to read landing and write/delete files for archive/quarantine behavior.

## SQL database permissions

Azure SQL also has its own database authorization. Giving ADF Azure RBAC does not automatically create a SQL database user. That is why this POC runs:

```sql
CREATE USER [ADF_NAME] FROM EXTERNAL PROVIDER;
```

then grants only required SQL permissions.

## Azure Key Vault

Key Vault stores secrets/keys/certificates when a secret is genuinely required. It is present for learning, but the main ADF->ADLS and ADF->SQL paths use Managed Identity so they do not need a password secret.

## Azure Monitor / Log Analytics

ADF Monitor gives immediate pipeline/activity run information. Log Analytics is optional for centralized diagnostic queries and longer-running monitoring patterns, but it can add ingestion cost.

## Terraform

Terraform lets you describe infrastructure in code, preview changes with `plan`, apply them, and recreate environments consistently.

## Bicep

Bicep is Azure's native declarative infrastructure language. This POC includes a small storage comparison so you can see the difference from Terraform without trying to learn both deeply at the same time.
