/* POC-01 verification queries */

-- 1. Curated row count (default 30-row generator => expected 28)
SELECT COUNT(*) AS curated_count
FROM dbo.orders;

-- 2. Staging should be empty after successful stored procedure
SELECT COUNT(*) AS staging_count
FROM dbo.orders_stg;

-- 3. Business-rule rejects (default generator => expected 1 negative-quantity row)
SELECT COUNT(*) AS sql_reject_count
FROM dbo.orders_rejects;

SELECT TOP (100)
    reject_id,
    order_id,
    quantity,
    unit_price,
    status,
    source_file,
    pipeline_run_id,
    reject_reason,
    reject_ts
FROM dbo.orders_rejects
ORDER BY reject_ts DESC;

-- 4. File-level control table
SELECT *
FROM dbo.etl_file_log
ORDER BY processed_ts DESC;

-- 5. Watermark/freshness evidence
SELECT *
FROM dbo.etl_watermark;

-- 6. Duplicate business key check: must return zero rows
SELECT order_id, COUNT(*) AS duplicate_count
FROM dbo.orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 7. Curated data preview
SELECT TOP (50) *
FROM dbo.orders
ORDER BY order_id;
GO
