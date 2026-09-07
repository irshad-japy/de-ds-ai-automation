# Troubleshooting

## 1. ADLS authorization error

Check Azure RBAC and Unity Catalog separately.

Azure:

- storage account -> IAM
- Access Connector managed identity -> `Storage Blob Data Contributor`

Databricks:

- storage credential points to the correct Access Connector
- external location URL is correct
- your user has required external-location privileges

## 2. `Path does not exist`

Check container name and source directory:

```text
abfss://poc02@<storage>.dfs.core.windows.net/raw/orders
abfss://poc02@<storage>.dfs.core.windows.net/raw/customers
```

## 3. Auto Loader new-column error

During phase 2, `sales_channel` is intentionally new.

Because `cloudFiles.schemaEvolutionMode=addNewColumns`, the stream can stop after updating its schema metadata. Rerun the Bronze notebook.

## 4. Bronze duplicates after rerun

Do not delete or change the checkpoint between normal runs.

Check that every source uses its own checkpoint path:

```text
checkpoints/bronze_orders
checkpoints/bronze_customers
```

If you deliberately delete a checkpoint, Auto Loader can treat files as unseen depending on the rebuilt state. Only reset checkpoints as an explicit recovery/replay exercise.

## 5. Silver duplicate order IDs

Run:

```sql
SELECT order_id, COUNT(*)
FROM azde_poc.silver.orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

If rows appear, inspect the dedup window and `updated_at` source values.

## 6. CDF not enabled

```sql
SHOW TBLPROPERTIES azde_poc.gold.fact_orders;
```

Expected:

```text
delta.enableChangeDataFeed = true
```

## 7. CDF version error

```sql
DESCRIBE HISTORY azde_poc.gold.fact_orders;
```

Use a version that still exists in Delta history. CDF is not an infinite archive.

## 8. Catalog permission error

If you cannot create `azde_poc`, you need Unity Catalog `CREATE CATALOG` privilege or an administrator-created catalog. Do not silently fall back to Hive metastore because governance is part of this POC.

## 9. Job costs more than expected

- terminate classic all-purpose compute
- use job/serverless compute when available
- keep the sample small
- delete the POC resource group after completion if it contains nothing else
