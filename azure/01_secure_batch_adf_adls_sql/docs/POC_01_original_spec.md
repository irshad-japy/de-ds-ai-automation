# POC-01 — Secure Batch Landing Zone with ADF, ADLS Gen2 and Azure SQL

## Objective

Build a secure, parameterized batch ETL pipeline:

**Synthetic CSV → ADLS Gen2 landing → Azure Data Factory → Azure SQL staging/curated → monitoring**

## Business scenario

A retail company receives daily order files. The platform must ingest only new files, validate them, load a staging table, merge them into a curated table, and preserve the raw files for audit.

## Azure services

- Azure Resource Group
- Azure Storage / ADLS Gen2
- Azure Data Factory
- Azure SQL Database
- Azure Key Vault
- Microsoft Entra ID
- Managed Identity + RBAC
- Azure Monitor / Log Analytics
- Azure Cost Management
- Optional: Self-hosted Integration Runtime
- Optional advanced networking: VNET, Private Endpoint, Private Link
- IaC practice: Terraform primary; Bicep/ARM comparison; PowerShell validation

## Architecture

```text
Synthetic CSV
   |
   v
ADLS Gen2 /landing/orders/YYYY/MM/DD/
   |
   v
ADF Copy Activity
   |
   v
Azure SQL dbo.orders_stg
   |
   v
Stored procedure / MERGE
   |
   v
dbo.orders
   |
   +--> ADF Monitor / Azure Monitor / Log Analytics
```

## Cost guardrails

- Use a tiny Azure SQL serverless/basic-compatible development configuration available in your region.
- Run ADF only on demand.
- Use tens/hundreds of rows, not millions.
- Do not create an always-running SHIR VM; install SHIR on your own Windows machine only for the optional lab.
- Private endpoints can add cost/complexity; learn the architecture first and deploy them only if budget permits.
- Delete the full resource group after evidence capture.

## Step-by-step

### 1. Create a resource group

Example naming:

```text
rg-azde-poc01-dev
```

Add tags:

```text
project=azure-poc
environment=dev
owner=personal
autoDelete=true
```

### 2. Create a Cost Management budget

Create a small monthly budget and email thresholds. The goal is awareness, not exact cost forecasting.

### 3. Create ADLS Gen2

Create a StorageV2 account with hierarchical namespace enabled.

Containers:

```text
landing
archive
quarantine
```

Folder convention:

```text
landing/orders/2026/08/28/orders_001.csv
```

### 4. Generate synthetic data locally

Columns:

```text
order_id,customer_id,order_ts,product_id,quantity,unit_price,status
```

Create 20–100 rows. Include two deliberately bad rows for validation.

### 5. Create Azure SQL Database

Create:

```sql
CREATE TABLE dbo.orders_stg (
    order_id       BIGINT,
    customer_id    BIGINT,
    order_ts       DATETIME2,
    product_id     BIGINT,
    quantity       INT,
    unit_price     DECIMAL(12,2),
    status         VARCHAR(30),
    load_ts        DATETIME2 DEFAULT SYSUTCDATETIME()
);
```

Create a final `dbo.orders` table with `order_id` as the business key.

### 6. Create ADF and use Managed Identity

Enable the ADF system-assigned Managed Identity.

Grant only the required permissions to storage and SQL. Prefer identity-based access rather than storing passwords.

### 7. Build parameterized linked services/datasets

Parameters:

```text
p_container
p_folder
p_file
p_target_table
```

Do not hardcode real keys in JSON that will be exported to Git.

### 8. Build the pipeline

Suggested activities:

1. Get Metadata
2. If Condition: file exists
3. Copy Activity: CSV → `orders_stg`
4. Stored Procedure: validate/merge
5. Move/archive file
6. Failure path → quarantine/log

### 9. Implement watermark/incremental behavior

Create a control table:

```sql
CREATE TABLE dbo.etl_watermark (
    pipeline_name VARCHAR(100) PRIMARY KEY,
    last_success_ts DATETIME2
);
```

Update it only after a successful run.

### 10. Add idempotency

Rerunning the same file should not duplicate business rows.

Use `MERGE` or an update/insert transaction based on `order_id`.

### 11. Monitoring

Capture:

- ADF pipeline status
- rows read/written
- execution time
- failure reason
- SQL row counts
- freshness timestamp

Route diagnostics to Log Analytics if budget permits.

### 12. Optional SHIR lab

Install Self-hosted Integration Runtime on your Windows laptop.

Use a local CSV folder or local SQL Server as a source and copy a tiny dataset to ADLS/Azure SQL.

Do not open inbound public ports for this lab.

### 13. IaC mini-lab

- Provision the resource group/storage/Key Vault with Terraform.
- Recreate one resource with Bicep to compare syntax.
- Export an ARM template and inspect it; do not make ARM your main authoring experience.
- Use PowerShell/Azure CLI to list deployed resources and tags.

## Validation

- First run loads expected rows.
- Second run of the same file creates no duplicates.
- Bad rows are rejected/quarantined.
- Watermark changes only on success.
- Removing storage permission causes a controlled failure.
- Restoring RBAC allows retry to succeed.

## GitHub artifacts

Commit:

```text
README.md
architecture.md
sql/
  001_create_tables.sql
  002_merge_orders.sql
adf/
  pipeline_sanitized.json
infra/
  terraform/
  bicep/
docs/
  validation.md
.env.example
```

## Cleanup

Delete `rg-azde-poc01-dev` after exporting sanitized evidence.

## Interview questions

1. Why use ADLS landing before SQL?
2. How do you make an ADF pipeline idempotent?
3. What is a watermark?
4. Managed Identity vs Key Vault secret?
5. When would SHIR be required?
6. Why use staging before MERGE?
7. How would you scale this to thousands of files?
8. How would private endpoints change the design?

## CV text — USE ONLY AFTER COMPLETION

**Project:** Secure Metadata-Driven Azure Batch Ingestion

- Built a parameterized Azure Data Factory pipeline to ingest synthetic order files from ADLS Gen2 into Azure SQL staging and curated tables.
- Implemented watermark-based incremental loading, idempotent MERGE logic, quarantine handling and retry-safe orchestration.
- Secured data access using Microsoft Entra ID, Managed Identity, RBAC and Key Vault patterns.
- Added Azure monitoring, execution metrics, cost controls and reusable Terraform/Bicep deployment assets.
