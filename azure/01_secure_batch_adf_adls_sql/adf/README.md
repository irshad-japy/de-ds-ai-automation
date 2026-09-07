# ADF build guide — beginner step-by-step

Use the UI first. The JSON files in this folder are sanitized learning/reference artifacts and may need the current ADF Studio UI to regenerate connector-specific details for your subscription.

## 1. Linked service — ADLS Gen2

ADF Studio → **Manage** → **Linked services** → **New** → `Azure Data Lake Storage Gen2`.

Set:

```text
Name: LS_ADLS_GEN2_MI
Authentication type: System-assigned managed identity
Storage account: your POC storage account
```

Test connection.

If it fails with 403, verify ADF has `Storage Blob Data Contributor` on the Storage Account (or appropriate container scope).

## 2. Linked service — Azure SQL Database

Manage → Linked services → New → `Azure SQL Database`.

```text
Name: LS_AZURE_SQL_MI
Connector version: Recommended, if prompted
Server: <your-server>.database.windows.net
Database: sqldb-azde-poc01-dev
Authentication: System-assigned managed identity
Encrypt: mandatory/current secure default
Trust server certificate: false
```

Test connection.

If it fails, verify:

1. SQL server Microsoft Entra admin is configured.
2. `sql/003_create_adf_user.sql` was executed in the target database with the exact ADF resource name.
3. The SQL logical-server firewall allows access from Azure services for this beginner public-endpoint lab.

## 3. Dataset — `DS_ADLS_OrdersCsv`

Author → Datasets → New dataset → `Azure Data Lake Storage Gen2` → `DelimitedText`.

Linked service:

```text
LS_ADLS_GEN2_MI
```

Add dataset parameters:

```text
p_container String
p_folder    String
p_file      String
```

Connection / Location dynamic content:

```text
File system = @dataset().p_container
Directory   = @dataset().p_folder
File        = @dataset().p_file
```

Format:

```text
Column delimiter: comma
First row as header: true
Quote character: "
```

Import schema from a sample file if convenient, but do not put credentials in the JSON.

## 4. Dataset — `DS_ADLS_Binary`

New dataset → ADLS Gen2 → `Binary`.

Same three parameters:

```text
p_container
p_folder
p_file
```

Use the same dynamic location expressions. This dataset is for byte-for-byte archive/quarantine copies and Delete Activity.

## 5. Dataset — `DS_SQL_Table`

New dataset → `Azure SQL Database`.

Linked service:

```text
LS_AZURE_SQL_MI
```

Parameter:

```text
p_target_table String
```

Table:

```text
Schema = dbo
Table  = @dataset().p_target_table
```

## 6. Pipeline — `PL_INGEST_ORDERS_BATCH`

Add parameters:

```text
p_container     String default landing
p_folder        String default orders/2026/08/28
p_file          String default orders_001.csv
p_target_table  String default orders_stg
```

### Activity A — Get Metadata

Name:

```text
Get_Metadata_File
```

Dataset:

```text
DS_ADLS_OrdersCsv
```

Pass all three file parameters from the pipeline.

Field list:

```text
Exists
Size
Last modified
```

Using `exists` is useful because Get Metadata can return `exists: false` instead of failing when the object is missing.

### Activity B — If Condition: file exists

Name:

```text
If_File_Exists
```

Expression:

```adf
@activity('Get_Metadata_File').output.exists
```

Put the remaining processing activities in the **True** branch.

### Activity C — Lookup processed-file control table

Name:

```text
Lookup_Already_Processed
```

Source dataset:

```text
DS_SQL_Table
p_target_table = etl_file_log
```

Query dynamic content:

```adf
@concat(
  'SELECT COUNT(*) AS processed_count FROM dbo.etl_file_log WHERE source_file = ''',
  pipeline().parameters.p_container, '/',
  pipeline().parameters.p_folder, '/',
  pipeline().parameters.p_file,
  ''' AND status = ''SUCCEEDED'''
)
```

First row only = true.

### Activity D — If Condition: not already processed

Name:

```text
If_Not_Processed
```

Expression:

```adf
@equals(int(activity('Lookup_Already_Processed').output.firstRow.processed_count), 0)
```

Use the **True** branch for ingestion.

Use the **False** branch to move a duplicate re-upload to:

```text
archive/duplicates/<original-folder>/<file>
```

then delete the duplicate landing copy. This keeps the landing zone clean while proving no duplicate SQL rows were created.

### Activity E — Copy CSV to SQL staging

Name:

```text
Copy_CSV_To_Staging
```

Source dataset:

```text
DS_ADLS_OrdersCsv
```

Sink dataset:

```text
DS_SQL_Table
p_target_table = @pipeline().parameters.p_target_table
```

Source → **Additional columns**:

```text
source_file
  @concat(pipeline().parameters.p_container,'/',pipeline().parameters.p_folder,'/',pipeline().parameters.p_file)

pipeline_run_id
  @pipeline().RunId
```

Mapping:

```text
order_id        -> order_id
customer_id     -> customer_id
order_ts        -> order_ts
product_id      -> product_id
quantity        -> quantity
unit_price      -> unit_price
status          -> status
source_file     -> source_file
pipeline_run_id -> pipeline_run_id
```

Fault tolerance:

```text
Skip incompatible rows: enabled
Redirect/log incompatible rows: ADLS linked service LS_ADLS_GEN2_MI
Path: quarantine/adf-incompatible/<run id>
```

In dynamic content, use:

```adf
@concat('quarantine/adf-incompatible/', pipeline().RunId)
```

The non-numeric `NOT_A_PRICE` record is expected to be incompatible with the SQL decimal column and therefore skipped/logged rather than stopping the entire tiny lab copy.

### Activity F — Stored Procedure

Name:

```text
SP_Validate_Merge
```

Dependency: `Copy_CSV_To_Staging` succeeded.

Linked service:

```text
LS_AZURE_SQL_MI
```

Stored procedure:

```text
dbo.usp_merge_orders
```

Import parameters and pass:

```text
pipeline_name = @pipeline().Pipeline
source_file   = @concat(pipeline().parameters.p_container,'/',pipeline().parameters.p_folder,'/',pipeline().parameters.p_file)
run_id        = @pipeline().RunId
```

### Activity G — Archive raw file

Name:

```text
Copy_Landing_To_Archive
```

Dependency: Stored Procedure succeeded.

Binary source:

```text
container = pipeline p_container
folder    = pipeline p_folder
file      = pipeline p_file
```

Binary sink:

```text
container = archive
folder    = pipeline p_folder
file      = pipeline p_file
```

### Activity H — Delete the landing source

Name:

```text
Delete_Landing_File
```

Dependency: archive copy succeeded.

Dataset:

```text
DS_ADLS_Binary pointing at original landing file
```

Recursive = false.

Deleting happens **after** the archive copy. Never reverse these two dependencies.

## 7. Failure path

Create a Binary Copy Activity from landing to:

```text
quarantine/pipeline-failures/<RunId>/<original-folder>/<file>
```

Connect it from Copy/Stored Procedure using the red **Failure** dependency.

If the failure itself is caused by storage RBAC being removed, the quarantine copy may also be unable to read storage. That is expected for the controlled RBAC-negative test; the important evidence is the ADF failure message and unchanged SQL watermark.

## 8. Validate and publish

Use:

```text
Validate all
Publish all
```

Then Trigger now.

## 9. Current documentation note

ADF connector UI details can evolve. The JSON in this repo is deliberately sanitized and instructional. If ADF Studio rewrites a connector property after you create it in the UI, prefer the UI-generated current artifact, then sanitize it before committing to GitHub.

### Keep a handled failure marked as Failed

When you add a red Failure dependency to a quarantine activity, add a final **Fail** activity after the quarantine copy. Otherwise a handled error path can be confusing when interpreting pipeline status.

Use a clear error code/message such as:

```text
POC01_COPY_FAILED
POC01_MERGE_FAILED
```

For the storage-RBAC negative test, quarantine itself can also fail because ADF no longer has storage access. The original authorization failure remains the important evidence and the watermark still must not advance.
