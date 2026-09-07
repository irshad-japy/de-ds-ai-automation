# Monitoring — POC-01

## Minimum monitoring: ADF Monitor

You can complete this POC without paying for extra diagnostic ingestion.

ADF Studio → **Monitor** → Pipeline runs.

For every evidence run record:

- pipeline name,
- Run ID,
- start/end time,
- status,
- activity status,
- duration,
- rows read,
- rows written/copied,
- incompatible/skipped-row evidence when available,
- failure code/message for negative tests.

## SQL operational checks

Use:

```sql
SELECT COUNT(*) FROM dbo.orders;
SELECT COUNT(*) FROM dbo.orders_stg;
SELECT * FROM dbo.orders_rejects ORDER BY reject_ts DESC;
SELECT * FROM dbo.etl_file_log ORDER BY processed_ts DESC;
SELECT * FROM dbo.etl_watermark;
```

These give:

- target row count,
- whether transient staging was cleaned,
- semantic data-quality rejects,
- processed-file lineage/status,
- latest successful pipeline freshness.

## Optional Log Analytics

If budget permits:

1. Create `law-azde-poc01-dev`.
2. Data Factory resource → Diagnostic settings.
3. Create a diagnostic setting and route selected Data Factory logs/metrics to the workspace.
4. Use only the categories useful for the lab.
5. Verify ingestion and then delete the Resource Group after evidence capture.

Diagnostic category names can change, so select them from the current Portal rather than hardcoding stale category names into this beginner project.

## Example evidence table for your notes

| Run | File | Status | Rows read | Curated | SQL rejects | ADF incompatible | Duration |
|---|---|---|---:|---:|---:|---:|---|
| Run 1 | orders_001.csv | Succeeded | 30 | 28 | 1 | 1 | capture from Monitor |
| Run 2 duplicate | orders_001.csv | Succeeded/Skipped branch | 0 load | still 28 | unchanged | unchanged | capture |
| RBAC negative | orders_002.csv | Failed | n/a | unchanged | unchanged | n/a | capture |
