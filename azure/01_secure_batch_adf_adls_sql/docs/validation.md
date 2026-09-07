# Validation plan — POC-01

## Expected default test data

Command:

```powershell
python python/generate_orders.py --rows 30 --output data/generated/orders_001.csv
```

Expected classification:

| Category | Expected rows |
|---|---:|
| Total CSV rows | 30 |
| Type incompatible (`NOT_A_PRICE`) | 1 |
| SQL business-rule reject (`quantity=-2`) | 1 |
| Curated valid rows | 28 |

## Test matrix

| Test | Action | Expected result | Evidence |
|---|---|---|---|
| 1 | First pipeline run | Succeeds | ADF Monitor |
| 2 | Query `dbo.orders` | 28 rows | SQL result |
| 3 | Query `dbo.orders_stg` | 0 rows after merge cleanup | SQL result |
| 4 | Query `dbo.orders_rejects` | 1 negative-quantity row | SQL result |
| 5 | Check quarantine redirect | incompatible row/log evidence exists | ADLS path |
| 6 | Check archive | raw CSV preserved | ADLS path |
| 7 | Re-upload exact same file | no SQL duplicates | ADF Lookup + SQL count |
| 8 | Duplicate-key query | returns zero rows | SQL result |
| 9 | Remove ADF storage RBAC | pipeline fails safely | ADF failure |
| 10 | Query watermark after failed run | unchanged by failed run | SQL result |
| 11 | Restore RBAC + retry | succeeds | ADF Monitor |

## SQL verification

Run `sql/004_verification_queries.sql`.

Key expectations for the default 30-row file:

```text
curated_count = 28
staging_count = 0
sql_reject_count = 1
duplicate query = 0 rows
```

## Validate processed-file idempotency

The control key is the full logical source path, for example:

```text
landing/orders/2026/08/28/orders_001.csv
```

After a successful run, `dbo.etl_file_log` should contain exactly one successful record for that source file. A re-upload of that exact path should be recognized as already processed.

## Validate MERGE idempotency separately

Even though the file-control check skips duplicates early, `dbo.orders.order_id` is the business key and the stored procedure uses `MERGE` to update/insert rather than blindly append.

This gives two layers:

1. **file-level idempotency** — do not process an already-successful file again;
2. **business-key idempotency** — `order_id` cannot create duplicate curated rows.

## Watermark test

Query before a negative test:

```sql
SELECT * FROM dbo.etl_watermark;
```

Cause a controlled failure by temporarily removing ADF's storage role and triggering a new-file run.

Query again:

```sql
SELECT * FROM dbo.etl_watermark;
```

The failed run must not update `last_success_ts` because the watermark change is committed only in the successful SQL procedure transaction.
