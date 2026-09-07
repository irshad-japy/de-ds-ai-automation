# POC-02 — Azure Databricks Medallion Lakehouse with Incremental CDC

> **Terraform-first edition.** Infrastructure, Azure RBAC, the Databricks workspace, Unity Catalog objects, notebook imports, and Databricks Jobs are now provisioned with Terraform so this POC can be recreated and destroyed cleanly. The original manual Azure Portal steps are preserved later as an appendix for learning/troubleshooting.

## Recommended beginner execution — do these commands in order

From Windows **Command Prompt** in this project root:

```cmd
cmd\00_check_prerequisites.cmd
cmd\01_configure_terraform.cmd
cmd\02_terraform_apply.cmd
cmd\03_upload_phase1.cmd
cmd\04_open_phase1_job.cmd
```

After the Phase-1 job succeeds, validate Bronze/Silver/Gold using `sql\validation_queries.sql`, then continue:

```cmd
cmd\05_upload_phase2.cmd
cmd\06_open_phase2_job.cmd
```

Validate schema evolution, Delta MERGE, SCD Type 2 and CDF. When the POC is complete:

```cmd
cmd\07_destroy.cmd
```

For the detailed line-by-line explanation, read **`docs/TERRAFORM_GUIDE.md`**.

## What Terraform now manages

```text
Azure Resource Group
├── ADLS Gen2 + poc02 container + logical folders
├── Databricks Access Connector (system-assigned managed identity)
├── Storage Blob Data Contributor RBAC
└── Azure Databricks Premium workspace

Unity Catalog / Databricks provider
├── storage credential
├── external location
├── azde_poc catalog
│   ├── bronze
│   ├── silver
│   ├── gold
│   └── quarantine
├── six imported notebooks
├── POC02-Phase1-Medallion job
└── POC02-Phase2-Incremental-CDC job
```

The notebooks deliberately remain responsible for the Delta tables and data transformations, because those are the concepts you are practicing: Auto Loader checkpoints, quality/quarantine, deduplication, schema evolution, MERGE, SCD1/SCD2 and Change Data Feed.

## Updated project structure

```text
POC_02_DATABRICKS_MEDALLION_CDC_PROJECT/
├── README.md
├── PROJECT_SOURCE.md
├── .gitignore
├── terraform/
│   ├── versions.tf
│   ├── providers.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── databricks.tf
│   ├── outputs.tf
│   ├── terraform.tfvars.example
│   └── README.md
├── cmd/
│   ├── 00_check_prerequisites.cmd
│   ├── 01_configure_terraform.cmd
│   ├── 02_terraform_apply.cmd
│   ├── 03_upload_phase1.cmd
│   ├── 04_open_phase1_job.cmd
│   ├── 05_upload_phase2.cmd
│   ├── 06_open_phase2_job.cmd
│   ├── 07_destroy.cmd
│   ├── 08_show_status.cmd
│   └── 09_optional_install_databricks_cli.cmd
├── notebooks/
│   ├── 00_setup.py
│   ├── 01_bronze_ingest.py
│   ├── 02_silver_quality.py
│   ├── 03_gold_dimensions.py
│   ├── 04_cdf_consumer.py
│   └── 05_performance_governance.py
├── sample_data/
│   ├── phase1/...
│   └── phase2/...
├── sql/
│   ├── 01_unity_catalog_objects.sql
│   └── validation_queries.sql
└── docs/
    ├── TERRAFORM_GUIDE.md
    ├── original_manual_steps_from_user.md
    ├── data_quality_rules.md
    ├── expected_results.md
    ├── schema_evolution_exercise.md
    ├── tuning_notes.md
    ├── unity_catalog_notes.md
    ├── troubleshooting.md
    ├── terraform_troubleshooting.md
    └── interview_questions.md
```

## Fast verification checkpoints

### After `02_terraform_apply.cmd`

```cmd
cd terraform
terraform validate
terraform state list
terraform output
```

You should see AzureRM resources plus Databricks storage credential/external location/catalog/schemas/notebooks/jobs.

### After `03_upload_phase1.cmd`

Only the Phase-1 CSV files should be under `raw/orders` and `raw/customers`.

### After Phase-1 job

Verify:

- Bronze contains raw rows + `_ingest_ts`, `_source_file`, `_batch_id`.
- rerunning Phase 1 without new files does not duplicate Bronze input because of checkpoints.
- invalid rows are in quarantine with `error_reason`.
- Silver deduplicates `order_id` predictably.
- Gold fact/dim tables exist and CDF is enabled on `fact_orders`.

### After Phase-2 job

Verify:

- Bronze contains the new nullable `sales_channel` column.
- only new files are processed by Auto Loader.
- `MERGE` updates existing Gold current state and inserts new orders.
- SCD2 keeps old and current versions of the changed customer.
- CDF consumer writes changed rows to `azde_poc.gold.fact_orders_changes_audit`.

### After `07_destroy.cmd`

```cmd
az group show --name rg-azde-poc02
```

`ResourceGroupNotFound` means the POC Azure resource group is gone. `terraform state list` should also be empty.

## Terraform troubleshooting shortcuts

If `terraform` or `az` is not recognized, fix the CLI installation/PATH first; Python packages such as `azure-identity` do not install Azure CLI.

If `terraform apply` fails only while calling the newly created Databricks workspace or validating the external location, do **not** create duplicates manually in Portal. Confirm your Azure login/subscription and rerun `cmd\02_terraform_apply.cmd`; Terraform will reuse state and continue converging.

If Unity Catalog/metastore is missing, this workspace-level Terraform cannot create storage credentials/catalogs until a Unity Catalog metastore is attached. New workspaces are normally automatically enabled; see the manual appendix below if your account behaves differently.

If Phase-2 Bronze fails when `sales_channel` is discovered, that is the intended Auto Loader `addNewColumns` schema-evolution exercise. Rerun the Phase-2 job after the schema metadata has been updated.

For Terraform/CMD-specific errors, see `docs/terraform_troubleshooting.md`.

---

# Original full learning guide and manual Azure Portal alternative

The sections below are retained so you can understand what Terraform automated and use the Portal only for inspection/troubleshooting.

# PART A — Azure setup from scratch

## 3. Prerequisites

You need:

1. An Azure subscription.
2. Permission to create resources in a resource group.
3. Permission to assign an Azure RBAC role on the storage account. In a personal subscription you are commonly the owner.
4. A region where Azure Databricks is available.
5. This project extracted locally.

For the lab, keep all resources in the same Azure region when possible.

Suggested names; change them if Azure says a name is already taken:

```text
Resource group:         rg-azde-poc02
Storage account:        stazdepoc02<unique>
ADLS container:         poc02
Databricks workspace:   dbw-azde-poc02
Access connector:       ac-azde-poc02
Storage credential:     poc02_storage_cred
External location:      poc02_ext
Catalog:                azde_poc
Schemas:                bronze, silver, gold, quarantine
```

Storage account names must be globally unique and use lowercase letters/numbers.

---

## 4. Create the Azure Resource Group

Azure Portal steps:

1. Open **portal.azure.com**.
2. Search for **Resource groups**.
3. Click **Create**.
4. Select your subscription.
5. Resource group name: `rg-azde-poc02`.
6. Choose your preferred Azure region.
7. Click **Review + create**.
8. Click **Create**.

### Verify

Open the new resource group. It should exist even though it is empty.

---

## 5. Create ADLS Gen2 storage

1. In Azure Portal search **Storage accounts**.
2. Click **Create**.
3. Select `rg-azde-poc02`.
4. Enter a unique storage account name, for example `stazdepoc021234`.
5. Region: use the same region as the resource group/Databricks if possible.
6. Performance: **Standard**.
7. Redundancy: choose the cheapest development option acceptable to you, commonly **LRS** for a temporary POC.
8. Open the **Advanced** tab.
9. Enable **Hierarchical namespace**. This makes the account ADLS Gen2-capable.
10. Keep the remaining options at safe defaults unless your organization requires something else.
11. Click **Review + create** and **Create**.

### Verify hierarchical namespace

After deployment:

1. Open the storage account.
2. Check **Data Lake Storage / Hierarchical namespace** or the storage account configuration.
3. Confirm hierarchical namespace is enabled.

---

## 6. Create the ADLS container and directories

1. Open your storage account.
2. Open **Data storage > Containers**.
3. Click **+ Container**.
4. Name: `poc02`.
5. Keep anonymous access disabled/private.
6. Create it.

Inside the `poc02` container create these directories:

```text
raw/orders/
raw/customers/
checkpoints/
schema/
quarantine/
```

If the portal UI creates folders only after a file is uploaded, that is okay. The Databricks notebooks will also create technical paths as they run.

### ADLS path pattern used by this project

Replace the storage account name:

```text
abfss://poc02@<STORAGE_ACCOUNT>.dfs.core.windows.net/
```

Example:

```text
abfss://poc02@stazdepoc021234.dfs.core.windows.net/
```

---

## 7. Create an Access Connector for Azure Databricks

This project uses an Azure managed identity rather than a storage key or client secret.

1. In Azure Portal click **Create a resource**.
2. Search **Access Connector for Azure Databricks**.
3. Click **Create**.
4. Subscription: your subscription.
5. Resource group: `rg-azde-poc02`.
6. Name: `ac-azde-poc02`.
7. Region: same region as storage/Databricks when possible.
8. Use a **system-assigned managed identity**.
9. Click **Review + create** and **Create**.

### Copy its resource ID

Open the connector and copy its Azure **Resource ID**. It looks like:

```text
/subscriptions/<subscription-id>/resourceGroups/rg-azde-poc02/providers/Microsoft.Databricks/accessConnectors/ac-azde-poc02
```

You will use this in Databricks when creating the storage credential.

---

## 8. Grant the connector access to ADLS

1. Open your storage account.
2. Open **Access Control (IAM)**.
3. Click **Add > Add role assignment**.
4. Select role **Storage Blob Data Contributor**.
5. Click **Next**.
6. Assign access to **Managed identity**.
7. Click **Select members**.
8. Managed identity type: **Access Connector for Azure Databricks**.
9. Select `ac-azde-poc02`.
10. Click **Select**.
11. Click **Review + assign** twice.

### Why this role?

It lets the Databricks managed identity read and write objects in the storage account without storing a secret in code.

### Why this POC does not require Event Grid

The notebook uses Auto Loader's default **directory listing** mode for simplicity. File-notification mode can require additional cloud-event permissions and configuration. Add that later as an advanced exercise.

---

## 9. Create the Azure Databricks workspace

1. In Azure Portal search **Azure Databricks**.
2. Click **Create**.
3. Resource group: `rg-azde-poc02`.
4. Workspace name: `dbw-azde-poc02`.
5. Region: same region as storage if possible.
6. For workspace type, choose the lowest-cost development option available to your account:
   - **Serverless** if your subscription/region offers it and you want minimal compute administration, or
   - **Hybrid/classic** if serverless is not available.
7. You do not need customer-managed keys for this beginner lab.
8. Click **Review + create** then **Create**.
9. After deployment click **Launch Workspace**.

> Azure/Databricks UI names can change over time. The important outcome is: you can open the workspace and run a notebook on supported compute.

---

## 10. Verify Unity Catalog

In Databricks:

1. Open **Catalog** / **Catalog Explorer** in the left sidebar.
2. If you can see catalogs such as `main`, Unity Catalog is available.
3. Open a SQL notebook and run:

```sql
SELECT current_catalog(), current_schema();
SHOW CATALOGS;
```

### Expected

You get catalog results instead of a Unity Catalog-not-enabled error.

### If Unity Catalog is not available

Do not continue with a Hive-metastore-only workaround for this POC. The source POC specifically asks you to practice Unity Catalog. In the Databricks account console, create/attach a Unity Catalog metastore to the workspace or use a workspace that is already Unity Catalog-enabled.

---

## 11. Create a storage credential in Unity Catalog

Use Catalog Explorer because it is easiest for a beginner.

1. Databricks sidebar > **Catalog**.
2. Click **+ Add** or the create menu.
3. Choose **Create a credential** / **Storage credential**.
4. Name: `poc02_storage_cred`.
5. Credential type: **Azure Managed Identity**.
6. Enter the Access Connector resource ID copied earlier.
7. Create the credential.

You should not paste an Azure storage key into the notebook.

---

## 12. Create the external location

1. Databricks sidebar > **Catalog**.
2. Click **+ Add > Create an external location**.
3. Name: `poc02_ext`.
4. Storage type: **Azure**.
5. URL:

```text
abfss://poc02@<STORAGE_ACCOUNT>.dfs.core.windows.net/
```

6. Storage credential: `poc02_storage_cred`.
7. Create the external location.
8. Grant your own Databricks user the privileges needed for the lab:
   - `READ FILES`
   - `WRITE FILES`
   - `CREATE EXTERNAL TABLE`
   - `CREATE MANAGED STORAGE`

The owner of an external location may already have broad privileges, but explicitly checking the permissions makes troubleshooting easier.

### Verify the external location

Run in Databricks SQL:

```sql
DESCRIBE EXTERNAL LOCATION poc02_ext;
SHOW EXTERNAL LOCATIONS;
```

Also test reading the container after you upload phase-1 files:

```python
storage_account = "<STORAGE_ACCOUNT>"
base = f"abfss://poc02@{storage_account}.dfs.core.windows.net"
display(dbutils.fs.ls(f"{base}/raw/orders"))
```

If you get an authorization error, fix Azure RBAC or Unity Catalog external-location permissions before proceeding.

---

## 13. Create compute

### Serverless workspace

Use serverless notebook/job compute if available. You do not manually manage a VM cluster.

### Hybrid/classic workspace

1. Go to **Compute**.
2. Click **Create compute**.
3. Choose a supported Databricks Runtime with Unity Catalog support.
4. For this tiny POC, select the smallest development option your workspace allows.
5. Prefer a single-node development configuration if your workspace permits it.
6. Set **auto termination to 15 minutes** or another short development value.
7. Create/start the compute only when needed.

Do not choose large production compute for a few CSV files.

---

# PART B — Upload the project and phase-1 data

## 14. Upload/import the notebooks

You have two simple options.

### Option A — Workspace import

1. In Databricks click **Workspace**.
2. Create a folder such as `POC_02_DATABRICKS_MEDALLION_CDC`.
3. Import the `.py` files from the local `notebooks/` folder.

### Option B — Databricks Git folder

If you already pushed this project to GitHub, create a Databricks Git folder/Repo and clone it. This is better practice for source control.

No token or secret should be committed to Git.

---

## 15. Upload phase-1 sample data to ADLS

Use the Azure Portal storage browser.

Upload:

```text
sample_data/phase1/raw/orders/orders_batch_001.csv
```

to:

```text
poc02/raw/orders/orders_batch_001.csv
```

Upload:

```text
sample_data/phase1/raw/customers/customers_batch_001.csv
```

to:

```text
poc02/raw/customers/customers_batch_001.csv
```

Do **not** upload phase-2 files yet. Phase 2 is how you prove incremental ingestion, schema evolution, MERGE, SCD2 and CDF.

### Verify upload

In Azure Portal you should see both files in the correct directories.

Optional Databricks check:

```python
storage_account = "<STORAGE_ACCOUNT>"
base = f"abfss://poc02@{storage_account}.dfs.core.windows.net"
display(dbutils.fs.ls(f"{base}/raw/orders"))
display(dbutils.fs.ls(f"{base}/raw/customers"))
```

---

# PART C — Run the notebooks

## 16. Notebook parameters

Every notebook uses simple widgets.

Use:

```text
storage_account = your real storage account name
container       = poc02
catalog         = azde_poc
```

For `01_bronze_ingest.py`, also set a batch label such as:

```text
batch_id = phase1
```

---

## 17. Run `00_setup.py`

Purpose:

- validates the ADLS base path
- creates catalog `azde_poc` with managed storage under `poc02/managed/azde_poc`
- creates schemas `bronze`, `silver`, `gold`, `quarantine`
- prints the paths that the remaining notebooks use

### Expected verification

Run:

```sql
SHOW CATALOGS;
SHOW SCHEMAS IN azde_poc;
```

Expected schemas include:

```text
bronze
silver
gold
quarantine
```

If `CREATE CATALOG` fails, check both `CREATE CATALOG` on the metastore and `CREATE MANAGED STORAGE` on `poc02_ext`. If your environment requires an administrator-created catalog, use that approved catalog and change the `catalog` widget consistently.

---

## 18. Run `01_bronze_ingest.py` for phase 1

Set:

```text
storage_account = <your storage account>
container       = poc02
catalog         = azde_poc
batch_id        = phase1
```

Then run all cells.

### What the notebook does

For both orders and customers it uses:

```python
spark.readStream.format("cloudFiles")
```

with:

- `cloudFiles.format = csv`
- schema tracking under `schema/...`
- streaming checkpoint under `checkpoints/...`
- `trigger(availableNow=True)` so it processes all currently available files and stops
- audit fields:
  - `_ingest_ts`
  - `_source_file`
  - `_batch_id`

The Bronze values remain strings as much as possible.

### Verify Bronze

Run:

```sql
SELECT * FROM azde_poc.bronze.orders ORDER BY _ingest_ts, order_id;
SELECT * FROM azde_poc.bronze.customers ORDER BY _ingest_ts, customer_id;
```

You should see phase-1 records with `_batch_id = 'phase1'`.

### Prove checkpoint behavior

Run `01_bronze_ingest.py` **again without uploading any new file**.

Expected result:

- no duplicate copy of the old source file is ingested
- row count remains unchanged

Check:

```sql
SELECT COUNT(*) FROM azde_poc.bronze.orders;
SELECT _source_file, COUNT(*)
FROM azde_poc.bronze.orders
GROUP BY _source_file;
```

This is one of the most important validations in the POC.

---

## 19. Run `02_silver_quality.py`

Purpose:

1. convert raw strings to business types
2. validate data
3. write invalid rows to quarantine
4. deduplicate orders by `order_id`
5. keep the latest customer record by `customer_id`
6. MERGE valid current-state rows into Silver tables

### Orders quality rules

- `order_id` must not be blank/null
- `quantity > 0`
- `unit_price >= 0`
- `order_ts` and `updated_at` must parse as timestamps
- `status` must be one of:
  - `CREATED`
  - `PROCESSING`
  - `SHIPPED`
  - `CANCELLED`

### Customer quality rules

- `customer_id` must not be blank/null
- `customer_name` must not be blank/null
- `updated_at` must be a valid timestamp
- email, when present, must contain `@`

### Verify quarantine

```sql
SELECT * FROM azde_poc.quarantine.orders_invalid;
SELECT * FROM azde_poc.quarantine.customers_invalid;
```

The phase-1 orders file intentionally contains invalid rows. You should see human-readable `error_reason` values.

### Verify deduplication

The phase-1 input intentionally contains duplicate `O1002` rows with different `updated_at` values.

Run:

```sql
SELECT order_id, status, updated_at
FROM azde_poc.silver.orders
WHERE order_id = 'O1002';
```

Expected: only one `O1002` row, and it is the row with the latest `updated_at`.

Check all Silver duplicates:

```sql
SELECT order_id, COUNT(*) AS c
FROM azde_poc.silver.orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

Expected: zero rows.

---

## 20. Run `03_gold_dimensions.py` for phase 1

Purpose:

- creates/updates `gold.fact_orders`
- creates/updates `gold.dim_product` using SCD Type 1
- creates/updates `gold.dim_customer` using SCD Type 2
- uses Delta MERGE
- creates `fact_orders` with legacy Delta CDF enabled from table creation

### Verify fact table

```sql
SELECT *
FROM azde_poc.gold.fact_orders
ORDER BY order_id;
```

Verify calculated amount:

```sql
SELECT order_id, quantity, unit_price, order_amount
FROM azde_poc.gold.fact_orders
ORDER BY order_id;
```

### Verify SCD Type 1 product dimension

```sql
SELECT *
FROM azde_poc.gold.dim_product
ORDER BY product_id;
```

One current row per product is expected. Later product attribute updates replace the old value rather than preserve a second history row.

### Verify SCD Type 2 customer dimension

```sql
SELECT customer_id, customer_name, city, country,
       effective_from, effective_to, is_current
FROM azde_poc.gold.dim_customer
ORDER BY customer_id, effective_from;
```

After phase 1 each customer should normally have one current row.

### Verify CDF property

```sql
SHOW TBLPROPERTIES azde_poc.gold.fact_orders;
```

Look for:

```text
delta.enableChangeDataFeed = true
```

---

# PART D — Incremental update + schema evolution + SCD2 + CDF

## 21. Record phase-1 baseline counts

Run and save the results in your notes:

```sql
SELECT COUNT(*) AS bronze_orders FROM azde_poc.bronze.orders;
SELECT COUNT(*) AS silver_orders FROM azde_poc.silver.orders;
SELECT COUNT(*) AS fact_orders   FROM azde_poc.gold.fact_orders;

DESCRIBE HISTORY azde_poc.gold.fact_orders;
```

Take screenshots if you want evidence for your learning notes/GitHub README, but remove private IDs or sensitive account data before publishing.

---

## 22. Upload phase-2 files

Now upload:

```text
sample_data/phase2/raw/orders/orders_batch_002_schema_evolution.csv
```

to:

```text
poc02/raw/orders/orders_batch_002_schema_evolution.csv
```

And:

```text
sample_data/phase2/raw/customers/customers_batch_002_customer_change.csv
```

to:

```text
poc02/raw/customers/customers_batch_002_customer_change.csv
```

### What phase 2 changes

Orders phase 2:

- updates existing order `O1001`
- inserts new orders
- adds a new nullable source column: `sales_channel`

Customers phase 2:

- changes `C002.city` to demonstrate SCD Type 2
- adds a new customer

---

## 23. Run `01_bronze_ingest.py` for phase 2

Set:

```text
batch_id = phase2
```

Run all cells.

### Important expected schema-evolution behavior

The notebook intentionally uses:

```text
cloudFiles.schemaEvolutionMode = addNewColumns
```

For Auto Loader, a newly discovered column can cause the stream to stop after the schema metadata is updated. If the first phase-2 run fails with an unknown/new-field schema-evolution message:

1. read the error
2. confirm it refers to `sales_channel`
3. simply run the Bronze notebook again
4. the updated schema metadata is reused
5. the new column should then be present in Bronze

This is an intentional learning exercise, not necessarily a pipeline bug.

### Verify the new column

```sql
DESCRIBE TABLE azde_poc.bronze.orders;

SELECT order_id, sales_channel, _batch_id, _source_file
FROM azde_poc.bronze.orders
WHERE _batch_id = 'phase2'
ORDER BY order_id;
```

### Controlled schema contract

Silver and Gold intentionally do **not** automatically promote every Bronze source column. `sales_channel` remains a Bronze/raw schema-evolution example until a developer explicitly approves it in downstream contracts.

That is safer than silently allowing every source change to affect business tables.

---

## 24. Verify Auto Loader processed only the new files

Check source files in Bronze:

```sql
SELECT _source_file, _batch_id, COUNT(*) AS rows_loaded
FROM azde_poc.bronze.orders
GROUP BY _source_file, _batch_id
ORDER BY _source_file;
```

Expected:

- phase-1 file appears once
- phase-2 file appears once
- rerunning the notebook does not re-ingest either file because the checkpoint remembers processed files

Run the Bronze notebook one more time with no new file. Counts should remain unchanged.

---

## 25. Rerun `02_silver_quality.py`

This makes the latest valid, deduplicated current-state data available in Silver.

### Verify updated order

```sql
SELECT order_id, status, updated_at
FROM azde_poc.silver.orders
WHERE order_id = 'O1001';
```

Expected: the phase-2 version wins because it has the later `updated_at`.

### Verify current customer

```sql
SELECT customer_id, city, updated_at
FROM azde_poc.silver.customers
WHERE customer_id = 'C002';
```

Expected: `C002` contains the new city from phase 2.

---

## 26. Rerun `03_gold_dimensions.py`

This applies the new Silver state to Gold using MERGE/SCD logic.

### Verify fact MERGE insert vs update

```sql
SELECT order_id, status, updated_at
FROM azde_poc.gold.fact_orders
ORDER BY order_id;
```

Expected:

- `O1001` updated
- new phase-2 order IDs inserted
- existing unaffected orders remain

### Verify SCD Type 2 history

```sql
SELECT customer_id, city,
       effective_from, effective_to, is_current
FROM azde_poc.gold.dim_customer
WHERE customer_id = 'C002'
ORDER BY effective_from;
```

Expected for `C002`:

1. old city row: `is_current = false`, `effective_to` populated
2. new city row: `is_current = true`, `effective_to = null`

Validate only one current row per customer:

```sql
SELECT customer_id, SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_rows
FROM azde_poc.gold.dim_customer
GROUP BY customer_id
HAVING current_rows <> 1;
```

Expected: zero rows.

---

## 27. Run `04_cdf_consumer.py`

This notebook demonstrates Delta Change Data Feed from `gold.fact_orders`.

The lab uses **legacy table CDF**:

```text
delta.enableChangeDataFeed = true
```

This is deliberate because it is easy to reproduce across many Databricks runtimes. Newer Azure Databricks environments can also offer **automatic CDF** based on row tracking/row lineage; that newer capability has separate runtime/feature requirements. Do not confuse the two approaches.

### What the notebook does

1. reads `table_changes()` in batch for inspection
2. starts a Structured Streaming CDF reader
3. uses a dedicated checkpoint path
4. writes change records into:

```text
azde_poc.gold.fact_orders_changes_audit
```

5. uses `availableNow=True` so it processes currently available changes and stops

### Verify CDF metadata

```sql
SELECT _change_type, COUNT(*)
FROM table_changes('azde_poc.gold.fact_orders', 0)
GROUP BY _change_type
ORDER BY _change_type;
```

After the phase-2 update you should normally see change types such as:

```text
insert
update_preimage
update_postimage
```

The exact number depends on your source rows.

### Verify CDF consumer checkpoint

Run `04_cdf_consumer.py` again without another fact-table change.

Expected: it does not append the same change events again because its streaming checkpoint stores progress.

Check:

```sql
SELECT COUNT(*) FROM azde_poc.gold.fact_orders_changes_audit;
```

Record the count, rerun, and confirm it stays unchanged when no new changes exist.

---

# PART E — Validation, performance, governance and jobs

## 28. Run validation SQL

Open `sql/validation_queries.sql` in a Databricks SQL editor/notebook and execute sections one by one.

For exact expected row counts with the supplied fake files, see `docs/expected_results.md`.

The file checks:

- Bronze file-level counts
- Silver duplicates
- quarantine rows
- fact-table state
- SCD2 current-row rules
- table history
- CDF results
- table details
- query plan examples

Do not blindly run destructive cleanup statements from any file without reading them first.

---

## 29. Run `05_performance_governance.py`

This notebook shows concepts rather than benchmark numbers because the sample is tiny.

It inspects:

- partitions
- logical/physical query plans
- Delta table detail/history
- file counts and size metadata
- Unity Catalog grants

### What to learn for larger data

At 100 GB / 1 TB scale you would review:

- source file size distribution
- small-file compaction strategy
- partition pruning and whether partitioning is actually useful
- clustering/data-skipping options supported by your runtime/table type
- shuffle partitions
- broadcast vs shuffle joins
- skewed keys
- incremental processing boundaries
- job compute sizing
- Photon/serverless options where appropriate
- cost vs latency requirements

Do not create thousands of partitions for a dataset that contains only a few rows.

---

## 30. Practice Unity Catalog governance

In Catalog Explorer inspect:

```text
azde_poc.bronze.orders
azde_poc.silver.orders
azde_poc.gold.fact_orders
azde_poc.gold.dim_customer
azde_poc.gold.dim_product
```

Practice:

1. table/schema comments
2. ownership
3. permissions/grants using only your own account identity
4. lineage view after notebooks/jobs have read and written tables

Example safe SQL:

```sql
COMMENT ON TABLE azde_poc.gold.fact_orders
IS 'POC-02 business-ready order fact table';

SHOW GRANTS ON TABLE azde_poc.gold.fact_orders;
```

Do not grant broad permissions to public identities in a personal POC.

---

## 31. Create a Databricks job/workflow

After all notebooks work manually, automate them.

1. In Databricks open **Workflows > Jobs & Pipelines**.
2. Click **Create > Job**.
3. Name: `poc02_medallion_cdc`.
4. Add notebook task `setup` -> `00_setup.py`.
5. Add task `bronze` -> `01_bronze_ingest.py`; depend on `setup`.
6. Add task `silver` -> `02_silver_quality.py`; depend on `bronze`.
7. Add task `gold` -> `03_gold_dimensions.py`; depend on `silver`.
8. Add task `cdf_consumer` -> `04_cdf_consumer.py`; depend on `gold`.
9. Add notebook parameters to each task:

```text
storage_account=<your storage account>
container=poc02
catalog=azde_poc
```

For Bronze also pass:

```text
batch_id=job_run
```

10. Choose job/serverless compute recommended by the workspace instead of leaving large all-purpose compute running.
11. Click **Run now**.
12. Open the run and inspect each task output.

### Job verification

Expected task chain:

```text
setup -> bronze -> silver -> gold -> cdf_consumer
```

All tasks should become successful/green.

If a phase-2 Auto Loader run stops only because `addNewColumns` detected the new field, update/retry the Bronze task after the schema metadata has evolved. That event is part of the schema-evolution exercise.

---

# PART F — Final checklist

## 32. Required validation checklist

Mark every item before calling the POC complete.

- [ ] ADLS Gen2 storage account has hierarchical namespace enabled.
- [ ] `poc02` container exists.
- [ ] Access Connector managed identity has `Storage Blob Data Contributor`.
- [ ] Databricks workspace opens successfully.
- [ ] Unity Catalog is enabled.
- [ ] `poc02_storage_cred` exists.
- [ ] `poc02_ext` external location works.
- [ ] `azde_poc.bronze`, `.silver`, `.gold`, `.quarantine` exist.
- [ ] Phase-1 files loaded into Bronze.
- [ ] Re-running Bronze with no new file does not duplicate data.
- [ ] Invalid order rows appear in quarantine with `error_reason`.
- [ ] Duplicate `O1002` is resolved predictably in Silver.
- [ ] Gold fact table contains valid orders.
- [ ] `dim_product` demonstrates SCD1/current-state behavior.
- [ ] Phase 2 adds `sales_channel` to Bronze schema.
- [ ] Phase-2 new file is processed without reprocessing phase 1.
- [ ] `O1001` is updated via MERGE.
- [ ] New phase-2 orders are inserted via MERGE.
- [ ] `C002` has two SCD2 rows after its city change.
- [ ] Exactly one `C002` row has `is_current=true`.
- [ ] CDF returns insert/update change records.
- [ ] CDF consumer does not duplicate events on rerun.
- [ ] You inspected `DESCRIBE HISTORY` and a query plan.
- [ ] You inspected Unity Catalog grants/lineage if available.
- [ ] Job/workflow run is successful.
- [ ] Compute is terminated after testing if using classic compute.

---

# PART G — Troubleshooting

## 33. Common errors

### Error: `PERMISSION_DENIED` / cannot read `abfss://...`

Check both layers:

1. Azure storage account IAM:
   - `ac-azde-poc02` has `Storage Blob Data Contributor`
2. Unity Catalog:
   - storage credential uses the correct access connector
   - external location points to the correct storage/container
   - your user has required external-location privileges

Azure RBAC role assignment can take a short time to propagate. Retry after confirming configuration.

### Error: external location path not found

Check exact path:

```text
abfss://poc02@<storage-account>.dfs.core.windows.net/
```

Do not use the `blob.core.windows.net` endpoint for this ADLS/ABFS path.

### Error: Auto Loader discovers `sales_channel` and stops

Expected in the schema-evolution exercise when using `addNewColumns`.

Rerun `01_bronze_ingest.py`. Auto Loader's schema metadata should now contain the new column.

### Error: `CREATE CATALOG` denied

You need Unity Catalog privileges. Either get `CREATE CATALOG` permission from the metastore/account administrator or use an allowed existing catalog and consistently change the `catalog` widget.

### Error: `DELTA_CHANGE_DATA_FEED_NOT_ENABLED`

Check:

```sql
SHOW TBLPROPERTIES azde_poc.gold.fact_orders;
```

`delta.enableChangeDataFeed` must be `true`. The provided Gold notebook creates the table with CDF enabled before MERGE writes.

### Error: CDF starting version unavailable

CDF history follows Delta retention. For this fresh POC, use the versions still visible in:

```sql
DESCRIBE HISTORY azde_poc.gold.fact_orders;
```

Do not treat CDF as a forever audit archive. This project writes consumed changes to `fact_orders_changes_audit` if you need a persistent lab history.

### Error: quarantine table creation denied

The quarantine tables are external Delta tables under the `poc02_ext` path. Ensure you have:

- `WRITE FILES`
- `CREATE EXTERNAL TABLE`

on the external location. Catalog creation also needs `CREATE MANAGED STORAGE` on the external location because this POC stores managed Bronze/Silver/Gold tables under `managed/azde_poc`.

See `docs/troubleshooting.md` for more details.

---

# PART H — Cleanup

## 34. Stop compute first

If you used classic/hybrid compute:

1. Go to **Compute**.
2. Terminate the cluster.
3. Confirm it is not running.

Serverless compute does not require you to leave a cluster running, but still review job/query usage and costs.

## 35. Delete lab resources when finished

If the entire resource group exists only for this POC:

1. Azure Portal > Resource groups.
2. Open `rg-azde-poc02`.
3. Review all resources carefully.
4. Delete the resource group only when you are sure nothing else important is inside it.

This removes the storage account, access connector and Databricks workspace in that resource group.

---

# PART I — GitHub guidance

## 36. What is safe to commit

Safe:

- notebooks
- SQL
- docs
- tiny fake CSV sample data
- README

Never commit:

- Azure keys
- SAS tokens
- Databricks personal access tokens
- Entra client secrets
- workspace tokens
- real customer data
- connection strings containing secrets

Typical commands:

```bash
git init
git add .
git commit -m "Add Azure Databricks Medallion CDC POC"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

Review `git status` and the staged files before pushing.

---

# PART J — Reference behavior used by this POC

This project intentionally uses the following current Azure Databricks patterns:

1. **Auto Loader + Unity Catalog external location** for ADLS ingestion.
2. **Dedicated schema/checkpoint paths** under a Unity Catalog-governed external location.
3. **`trigger(availableNow=True)`** for an incremental workload that processes currently available files and then stops.
4. **Managed identity via Access Connector** rather than embedding storage secrets.
5. **Legacy Delta table CDF** (`delta.enableChangeDataFeed=true`) for broad, explicit lab compatibility.
6. **Managed Bronze/Silver/Gold tables** in Unity Catalog plus external Delta quarantine data under ADLS.

Microsoft/Databricks documentation used while preparing the project:

- Azure Databricks workspace creation: https://learn.microsoft.com/azure/databricks/admin/workspace/create-workspace
- ADLS Gen2 external location / storage credential: https://learn.microsoft.com/azure/databricks/connect/unity-catalog/cloud-storage/storage-credentials
- Auto Loader with Unity Catalog: https://learn.microsoft.com/azure/databricks/ingestion/cloud-object-storage/auto-loader/unity-catalog
- Auto Loader schema inference/evolution: https://learn.microsoft.com/azure/databricks/ingestion/cloud-object-storage/auto-loader/schema
- Change Data Feed: https://learn.microsoft.com/azure/databricks/tables/features/change-data-feed
- Lakeflow Jobs configuration: https://learn.microsoft.com/azure/databricks/jobs/configure-job

---

## 37. Completion result

When every checklist item passes, you have completed a hands-on Azure Databricks data-engineering project that covers the original POC-02 requirements:

```text
ADLS -> Auto Loader -> Bronze -> Silver -> Gold
                   -> quality/quarantine
                   -> dedup
                   -> schema evolution
                   -> Delta MERGE
                   -> SCD1/SCD2
                   -> CDF incremental consumer
                   -> Unity Catalog governance
                   -> performance/job monitoring
```

Use the CV bullets in the original POC specification only after you have personally completed and verified the lab.
