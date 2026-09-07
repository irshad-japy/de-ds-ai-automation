# Azure Portal build steps — POC-01

Use this as a slower click-by-click companion to the root `README.md`.

## Phase 1 — Resource group + budget

1. Sign in to Azure Portal.
2. Confirm the correct directory/tenant and subscription.
3. Search `Resource groups`.
4. Select **Create**.
5. Subscription: your personal POC subscription.
6. Resource group: `rg-azde-poc01-dev`.
7. Region: choose one supported region and reuse it where practical.
8. Add tags:
   - `project=azure-poc`
   - `environment=dev`
   - `owner=personal`
   - `autoDelete=true`
9. Review + create.
10. Open Cost Management at the subscription or resource-group scope.
11. Create a small monthly budget and email thresholds.

### Checkpoint

You should be able to answer: **What is a Resource Group?**

> A Resource Group is a logical lifecycle/security/management boundary for related Azure resources. In this POC it also makes cleanup easy because the whole lab can be removed together.

## Phase 2 — ADLS Gen2

1. Search `Storage accounts` → Create.
2. Put the account in `rg-azde-poc01-dev`.
3. Use Standard + LRS for the tiny lab.
4. Enable secure transfer.
5. Disable anonymous public blob access.
6. On Advanced/Data Lake options, enable **Hierarchical namespace**.
7. Create.
8. Open the Storage Account.
9. Create private containers/file systems:
   - `landing`
   - `archive`
   - `quarantine`

### Why ADLS before SQL?

The raw landing zone decouples file arrival from relational loading, preserves immutable-ish source evidence for replay/audit, and handles file-scale ingestion better than directly pushing every source file into the database.

## Phase 3 — ADF

1. Search `Data factories` → Create.
2. Name: `adf-azde-poc01-<unique>`.
3. Put it in the POC Resource Group.
4. Configure Git later for the first beginner run.
5. Create.
6. Open ADF resource → Properties / Managed identity.
7. Copy or note the system-assigned Managed Identity Object ID.

### Checkpoint

**Managed Identity** is an Azure-managed identity for a resource. ADF can request Entra tokens without you storing a password/client secret in pipeline JSON.

## Phase 4 — ADF RBAC on ADLS

1. Open Storage Account → Access control (IAM).
2. Add role assignment.
3. Role: `Storage Blob Data Contributor`.
4. Member type: Managed identity.
5. Select the system-assigned identity of your Data Factory.
6. Assign.
7. Repeat for your own user if you will run the Python uploader using `az login`.

### Least privilege note

ADF needs read + write + delete behavior across landing/archive/quarantine in this specific design. For a more granular enterprise design, scope roles/ACLs to specific containers/directories and split identities if required.

## Phase 5 — Azure SQL Database

1. Search `SQL databases` → Create.
2. Database: `sqldb-azde-poc01-dev`.
3. Create a new SQL logical server: `sql-azde-poc01-<unique>`.
4. Choose a small development compute tier available in your region.
5. Add a bootstrap SQL admin, but do not reuse the password anywhere else and never commit it.
6. Networking for beginner version:
   - Public endpoint enabled.
   - Add your client IP.
   - Allow Azure services/resources to access the server so ADF Azure Integration Runtime can reach it.
7. Create.

## Phase 6 — Microsoft Entra admin for SQL

1. Open the SQL logical server.
2. Find Microsoft Entra ID / Microsoft Entra admin.
3. Set a user/group you control as the admin.
4. Save.
5. Connect to the POC database using Entra authentication.
6. Run:
   - `sql/001_create_tables.sql`
   - `sql/002_merge_orders.sql`
   - edit and run `sql/003_create_adf_user.sql`

## Phase 7 — Key Vault

1. Search `Key vaults` → Create.
2. Name: `kv-azde-poc01-<unique>`.
3. Same Resource Group and region.
4. Prefer Azure RBAC permission model.
5. Keep safe deletion defaults.
6. Do not create a SQL-password secret merely to force Key Vault into the main data path; Managed Identity is the preferred approach here.

## Phase 8 — Upload a sample file

1. Generate locally with `python/generate_orders.py`.
2. Run `az login`.
3. Give your own Entra user Storage Blob Data Contributor.
4. Run `python/upload_to_adls.py`.
5. In Portal, verify the file under:
   `landing/orders/YYYY/MM/DD/orders_001.csv`.

## Phase 9 — ADF authoring

1. ADF → Launch Studio.
2. Manage → Linked Services:
   - `LS_ADLS_GEN2_MI`
   - `LS_AZURE_SQL_MI`
3. Author → Datasets:
   - `DS_ADLS_OrdersCsv`
   - `DS_ADLS_Binary`
   - `DS_SQL_Table`
4. Author → Pipeline:
   - `PL_INGEST_ORDERS_BATCH`
5. Add pipeline parameters.
6. Build activity graph from `adf/README.md`.
7. Validate all.
8. Publish all.
9. Trigger now.

## Phase 10 — Observe the run

ADF Studio → Monitor:

1. Open the pipeline run.
2. Open each activity output.
3. Record rows read/written, duration, status, and failure details.
4. Compare ADF numbers with SQL row counts.
5. Verify archive/quarantine paths.

## Phase 11 — Negative RBAC test

Only after successful testing:

1. Remove ADF's Storage Blob Data Contributor role.
2. Run a new test file.
3. Confirm controlled access failure.
4. Confirm watermark does not advance.
5. Restore the role.
6. Retry and confirm success.

## Phase 12 — Cleanup

1. Save only sanitized screenshots/evidence.
2. Check Git for secrets.
3. Delete `rg-azde-poc01-dev` after the lab.
