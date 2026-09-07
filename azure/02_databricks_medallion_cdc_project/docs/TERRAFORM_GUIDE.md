# POC-02 Terraform execution guide — Windows CMD

This is the **recommended execution path** for this project. The original manual Azure Portal flow is kept in the root README as a learning/reference appendix, but Terraform now provisions and destroys the lab infrastructure.

## What Terraform creates

```text
Azure subscription
└── Resource Group: rg-azde-poc02
    ├── ADLS Gen2 Storage Account: stazdepoc02<random>
    │   └── container: poc02
    │       ├── raw/orders/
    │       ├── raw/customers/
    │       ├── checkpoints/
    │       ├── schema/
    │       ├── quarantine/
    │       └── managed/
    ├── Access Connector: ac-azde-poc02
    │   └── System Assigned Managed Identity
    └── Azure Databricks Workspace: dbw-azde-poc02 (Premium)

Azure RBAC
├── Access Connector -> Storage Blob Data Contributor on ADLS
└── Current az-login identity -> Storage Blob Data Contributor on ADLS

Azure Databricks / Unity Catalog
├── Storage Credential: poc02_storage_cred
├── External Location: poc02_ext
├── Catalog: azde_poc
│   ├── bronze
│   ├── silver
│   ├── gold
│   └── quarantine
├── /Shared/POC_02_DATABRICKS_MEDALLION_CDC/* notebooks
├── Job: POC02-Phase1-Medallion
└── Job: POC02-Phase2-Incremental-CDC
```

## Important separation of responsibilities

Terraform builds infrastructure/governance/workspace assets. The PySpark notebooks build and modify Delta tables because you need to see Auto Loader checkpoints, validation, deduplication, Delta MERGE, SCD1/SCD2 and CDF happening as part of the POC.

## Step 0 — Install prerequisites

Install these once on Windows:

```cmd
az --version
terraform version
```

If `az` is not recognized, install **Azure CLI**. Python package `azure-identity` does **not** install the `az` command.

For Terraform, install the Terraform CLI and reopen CMD so `terraform.exe` is on PATH.

You can verify both using:

```cmd
cmd\00_check_prerequisites.cmd
```

## Step 1 — Login and generate terraform.tfvars

From the project root:

```cmd
cmd\01_configure_terraform.cmd
```

The script:

1. runs `az login` when necessary;
2. lists subscriptions;
3. asks for the subscription ID;
4. runs `az account set`;
5. asks for an Azure region (default `centralindia`);
6. generates `terraform\terraform.tfvars`.

Verify:

```cmd
az account show --output table
type terraform\terraform.tfvars
```

Do **not** commit `terraform.tfvars` if you later add sensitive values. This POC file contains no secrets, but it is ignored to keep local configuration separate.

## Step 2 — Terraform init, validate, plan and apply

Run:

```cmd
cmd\02_terraform_apply.cmd
```

The script executes:

```cmd
cd terraform
terraform init -upgrade
terraform fmt -recursive
terraform validate
terraform plan -out=poc02.tfplan
terraform apply poc02.tfplan
terraform output
```

### What to verify after apply

```cmd
cd terraform
terraform state list
terraform output
```

Expected state categories include:

- `azurerm_resource_group.poc02`
- `azurerm_storage_account.adls`
- `azurerm_storage_container.poc02`
- `azurerm_databricks_access_connector.poc02`
- `azurerm_databricks_workspace.poc02`
- `databricks_storage_credential.poc02`
- `databricks_external_location.poc02`
- `databricks_catalog.poc02`
- four `databricks_schema` resources
- six `databricks_notebook` resources
- two `databricks_job` resources

You can also run:

```cmd
cmd\08_show_status.cmd
```

### If apply fails while first connecting to Databricks

A freshly created workspace and Azure role assignment can take a short period to become usable by all control/data-plane APIs. The Terraform configuration already includes an RBAC dependency delay. If the error is clearly workspace readiness or storage permission propagation, keep the state and rerun:

```cmd
cmd\02_terraform_apply.cmd
```

Do not manually recreate the same resources in Portal; let Terraform converge the state.

### Unity Catalog verification

Terraform calls `databricks_current_metastore`. New Azure Databricks workspaces are normally Unity Catalog enabled automatically. If Terraform reports no metastore/Unity Catalog, see the root README troubleshooting appendix; account-level metastore assignment may need attention before this workspace-level Terraform can continue.

## Step 3 — Upload only Phase-1 source files

Run:

```cmd
cmd\03_upload_phase1.cmd
```

It uploads:

```text
sample_data/phase1/raw/orders/orders_batch_001.csv
  -> abfss://poc02@<storage>.dfs.core.windows.net/raw/orders/orders_batch_001.csv

sample_data/phase1/raw/customers/customers_batch_001.csv
  -> abfss://poc02@<storage>.dfs.core.windows.net/raw/customers/customers_batch_001.csv
```

The command uses Azure Entra authentication:

```cmd
az storage fs file upload --auth-mode login ...
```

Terraform grants the current `az login` identity `Storage Blob Data Contributor` so no account key is embedded in scripts.

### Verify Phase 1 upload

The script lists `raw/orders` and `raw/customers`. You can also manually run:

```cmd
cd terraform
for /f "delims=" %A in ('terraform output -raw storage_account_name') do set STORAGE_ACCOUNT=%A
az storage fs file list --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system poc02 --path raw/orders --output table
az storage fs file list --account-name "%STORAGE_ACCOUNT%" --auth-mode login --file-system poc02 --path raw/customers --output table
```

At this point **do not upload Phase 2**.

## Step 4 — Run the Phase-1 Databricks job

Run:

```cmd
cmd\04_open_phase1_job.cmd
```

This opens the Terraform-created Databricks job. Click **Run now**.

Task dependency chain:

```text
setup -> bronze -> silver -> gold
```

Terraform already passes these notebook parameters:

```text
storage_account = Terraform-generated ADLS name
container       = poc02
catalog         = azde_poc
batch_id        = phase1 (Bronze task)
```

### Phase-1 validation

Run the validation SQL from `sql/validation_queries.sql` in a Databricks SQL editor/notebook, or use the notebook checks described in the root README.

High-value checks:

```sql
SELECT COUNT(*) FROM azde_poc.bronze.orders;
SELECT COUNT(*) FROM azde_poc.silver.orders;
SELECT * FROM azde_poc.quarantine.orders ORDER BY order_id;
SELECT * FROM azde_poc.gold.fact_orders ORDER BY order_id;
SELECT * FROM azde_poc.gold.dim_customer ORDER BY customer_id, effective_from;
DESCRIBE HISTORY azde_poc.gold.fact_orders;
```

Expected behavior from the supplied sample data is documented in `docs/expected_results.md`.

### Prove checkpoint idempotency

Before Phase 2, rerun **POC02-Phase1-Medallion** once without adding new files. Bronze should not re-ingest the same Phase-1 input files because Auto Loader uses the checkpoint locations under `checkpoints/`.

## Step 5 — Upload Phase-2 incremental files

Only after Phase-1 validation:

```cmd
cmd\05_upload_phase2.cmd
```

This adds:

```text
orders_batch_002_schema_evolution.csv
customers_batch_002_customer_change.csv
```

Phase 2 demonstrates:

- a new nullable `sales_channel` source column;
- new orders;
- an update to an existing order;
- a customer attribute change used for SCD Type 2;
- downstream CDF consumption.

## Step 6 — Run Phase-2 incremental/CDC job

```cmd
cmd\06_open_phase2_job.cmd
```

Click **Run now**.

Task dependency chain:

```text
bronze_incremental -> silver_refresh -> gold_merge_scd -> cdf_consumer
```

### Expected schema-evolution restart

The Bronze notebook deliberately uses:

```python
.option("cloudFiles.schemaEvolutionMode", "addNewColumns")
```

When `sales_channel` is first detected, Auto Loader may stop that run after updating the tracked schema. This is the expected lab behavior. Rerun the Phase-2 job; the checkpoint/schema metadata ensures the new batch is then processed without re-reading already processed files.

## Step 7 — Verify incremental processing, MERGE, SCD2 and CDF

Use `sql/validation_queries.sql` and verify:

```sql
-- New schema column exists in Bronze
DESCRIBE TABLE azde_poc.bronze.orders;

-- Same business order is not duplicated in current Silver/Gold state
SELECT order_id, COUNT(*)
FROM azde_poc.silver.orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Gold current state
SELECT *
FROM azde_poc.gold.fact_orders
ORDER BY order_id;

-- SCD2 customer history; changed customer should have old + current rows
SELECT customer_id, city, effective_from, effective_to, is_current
FROM azde_poc.gold.dim_customer
ORDER BY customer_id, effective_from;

-- CDF audit generated by downstream consumer
SELECT *
FROM azde_poc.gold.fact_orders_changes_audit
ORDER BY _commit_version, order_id;
```

Also inspect the Databricks Job run UI for:

- task success/failure;
- Spark stages;
- shuffle information;
- executor/driver metrics;
- query plans from `05_performance_governance.py`.

## Step 8 — Run performance/governance notebook

Terraform imported `05_performance_governance` into:

```text
/Shared/POC_02_DATABRICKS_MEDALLION_CDC/05_performance_governance
```

Run it interactively after Phase 2. Use the same Terraform-created job compute configuration as a reference if you create temporary interactive compute. Terminate interactive compute when finished.

Verify in Catalog Explorer:

```text
azde_poc
├── bronze
├── silver
├── gold
└── quarantine
```

Also inspect:

- external location `poc02_ext`;
- storage credential `poc02_storage_cred`;
- catalog/schema comments;
- lineage for tables touched by notebooks.

## Step 9 — Terraform drift/change practice

Make a harmless Terraform change, for example update a schema comment, then run:

```cmd
cd terraform
terraform plan
terraform apply
```

This teaches the important Terraform workflow:

```text
configuration -> plan -> apply -> state
```

Do **not** modify resource names mid-POC unless you understand that Terraform may replace resources.

## Step 10 — Full cleanup with Terraform

When every validation is complete:

```cmd
cmd\07_destroy.cmd
```

The script requires you to type `DESTROY`, then runs:

```cmd
cd terraform
terraform plan -destroy -out=poc02-destroy.tfplan
terraform apply poc02-destroy.tfplan
```

Terraform first destroys managed Databricks workspace objects, including the POC catalog (`force_destroy = true` so notebook-created tables inside the POC catalog do not block deletion), then removes Azure infrastructure tracked in the state.

### Verify cleanup

```cmd
az group show --name rg-azde-poc02
```

If Azure returns ResourceGroupNotFound, cleanup is complete.

You can also check:

```cmd
cd terraform
terraform state list
```

It should return no managed resources after successful destruction.

## Terraform files explained

| File | Purpose |
|---|---|
| `versions.tf` | Terraform and provider version constraints |
| `providers.tf` | AzureRM + Databricks providers using Azure CLI auth |
| `variables.tf` | Beginner-editable settings |
| `main.tf` | Azure RG, ADLS, Access Connector, RBAC, workspace |
| `databricks.tf` | UC objects, notebook imports, Phase-1/Phase-2 jobs |
| `outputs.tf` | Names/URLs/job IDs needed for verification and scripts |
| `terraform.tfvars.example` | Safe example config; real tfvars is locally generated |

## Cost guardrails

- Job compute is ephemeral: Databricks creates it for the job run and terminates it after the run.
- The sample data is tiny.
- ADLS uses Standard LRS.
- Do not leave additional interactive compute running.
- Destroy the POC when finished.

## GitHub safety

Safe to commit:

```text
terraform/*.tf
terraform/terraform.tfvars.example
cmd/*.cmd
notebooks/
sample_data/
sql/
docs/
```

Do not commit:

```text
terraform/.terraform/
terraform/*.tfstate*
terraform/*.tfplan
terraform/terraform.tfvars
crash.log
Databricks tokens
Azure client secrets
Storage account keys/SAS tokens
```

## More troubleshooting

See `docs/terraform_troubleshooting.md` for Azure CLI, Terraform, RBAC, Unity Catalog, ADLS upload, compute quota, schema-evolution, and destroy errors.
