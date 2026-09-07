# POC-02 — Azure Databricks Medallion Lakehouse with Incremental CDC

## Objective

Build a Bronze/Silver/Gold lakehouse and demonstrate incremental processing, schema evolution and Delta change processing.

## Services and skills

- Azure Databricks
- ADLS Gen2
- PySpark
- Spark SQL
- Delta Lake
- Auto Loader pattern
- Delta MERGE
- Change Data Feed (CDF)
- CDC/SCD Type 1 and Type 2
- data quality/quarantine
- partitioning
- Unity Catalog
- job monitoring and tuning

## Architecture

```text
ADLS landing
   |
   v
Bronze Delta  -- raw + audit columns
   |
   v
Silver Delta  -- validation + dedup + standardization
   |
   v
Gold Delta    -- fact/dimension model
   |
   +--> CDF / incremental consumers
```

## Cost guardrails

- Create compute only while actively using it.
- Choose the smallest supported development/serverless option available to the account.
- Terminate compute immediately after the lab.
- Use hundreds or a few thousand rows.

## Steps

### 1. Reuse or create an ADLS Gen2 account

Folders:

```text
raw/orders/
raw/customers/
checkpoints/
quarantine/
```

### 2. Create Databricks workspace

Verify whether Unity Catalog is enabled.

Learn the namespace:

```text
catalog.schema.table
```

Create a small logical structure such as:

```text
azde_poc.bronze.orders
azde_poc.silver.orders
azde_poc.gold.fact_orders
azde_poc.gold.dim_customer
```

### 3. Bronze ingestion

Add ingestion metadata:

```text
_ingest_ts
_source_file
_batch_id
```

Preserve source values with minimal transformations.

### 4. Auto Loader pattern

Implement an incremental file ingestion notebook using the current supported Auto Loader pattern in your workspace.

Checkpoint under a dedicated path.

Key interview point: a checkpoint tracks stream/incremental state; it is not business data.

### 5. Silver quality rules

Examples:

- `order_id IS NOT NULL`
- `quantity > 0`
- `unit_price >= 0`
- valid timestamp
- status in an allowed list

Write invalid records to quarantine with `error_reason`.

### 6. Deduplicate

Use a window keyed by `order_id`, keeping the latest record by source/update timestamp.

### 7. Schema evolution exercise

Add one new nullable column in a later input file.

Document:

- what changed;
- how the pipeline reacted;
- how you controlled schema evolution;
- why unrestricted schema drift is risky.

### 8. Gold model

Create:

```text
fact_orders
dim_customer
dim_product
```

Use business-friendly types and column names.

### 9. SCD Type 1

For a simple current-state dimension, update the latest attribute value.

### 10. SCD Type 2

For a historical dimension, add:

```text
effective_from
effective_to
is_current
```

Demonstrate one customer attribute change.

### 11. Delta MERGE

Use MERGE for upserts from Silver to Gold.

Validate inserts vs updates.

### 12. Change Data Feed

Enable/use the supported CDF approach available in your workspace and show how a downstream consumer reads only changed rows.

Keep the README explicit about whether you used legacy table CDF or newer workspace/runtime capabilities.

### 13. Performance lab

With a tiny dataset, the goal is concepts, not benchmark numbers.

Inspect:

- number of partitions
- shuffle
- join strategy
- file sizes
- query plan

Write down what you would change at 100 GB / 1 TB scale.

### 14. Unity Catalog governance

Practice:

- catalog/schema/table organization
- grants
- lineage view
- tags/comments
- table ownership

Use only your own account identities.

## Validation

- New files load without reprocessing old files.
- Duplicate order IDs are resolved predictably.
- Invalid rows go to quarantine.
- Schema change is documented.
- MERGE produces correct current state.
- SCD2 preserves history.
- CDF returns changed records.
- Lineage is visible if enabled.

## GitHub artifacts

```text
notebooks/
  01_bronze_ingest.py
  02_silver_quality.py
  03_gold_dimensions.py
  04_cdf_consumer.py
sql/
  validation_queries.sql
docs/
  data_quality_rules.md
  tuning_notes.md
  unity_catalog_notes.md
```

Do not export workspace tokens.

## Cleanup

Terminate compute first. Delete the workspace/resource group if it exists only for this POC.

## Interview questions

1. Bronze vs Silver vs Gold?
2. Auto Loader vs batch file listing?
3. What makes a streaming job exactly-once/idempotent in practice?
4. MERGE vs overwrite?
5. CDF vs CDC?
6. SCD1 vs SCD2?
7. What does a checkpoint contain?
8. How do small files hurt Spark?
9. How does Unity Catalog improve governance?

## CV text — USE ONLY AFTER COMPLETION

- Built an Azure Databricks PySpark/Delta Lake Medallion pipeline with incremental ingestion, data quality, quarantine and schema evolution controls.
- Implemented Delta MERGE, CDC/CDF, deduplication and SCD Type 1/2 patterns for reliable curated data.
- Applied Unity Catalog organization, access controls and lineage concepts across Bronze/Silver/Gold assets.
- Documented Spark partitioning, join and file-layout tuning decisions with rerunnable validation queries.
