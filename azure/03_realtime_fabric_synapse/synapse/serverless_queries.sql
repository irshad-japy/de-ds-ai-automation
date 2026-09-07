/*
POC-03 - Synapse serverless SQL over Gold Parquet

Run this in the built-in serverless SQL pool of a Synapse workspace.

Before running:
1. Replace <storage-account>.
2. Ensure your signed-in identity has appropriate read permission on the ADLS path.
3. If your environment requires credentials, follow your organization's credential pattern.
*/

-- A. Simple smoke test: scan the Gold Parquet folder.
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://<storage-account>.dfs.core.windows.net/realtime/gold/shipment_summary/*.parquet',
    FORMAT = 'PARQUET'
) AS rows;

-- B. Cost-aware query: read only columns needed by the report.
SELECT
    region,
    total_orders,
    delayed_shipments,
    revenue
FROM OPENROWSET(
    BULK 'https://<storage-account>.dfs.core.windows.net/realtime/gold/shipment_summary/*.parquet',
    FORMAT = 'PARQUET'
)
WITH (
    region VARCHAR(50),
    total_orders BIGINT,
    revenue FLOAT,
    delayed_shipments BIGINT
) AS gold
ORDER BY region;

-- C. Business check.
SELECT
    SUM(total_orders) AS total_orders,
    ROUND(SUM(revenue), 2) AS revenue,
    SUM(delayed_shipments) AS delayed_shipments
FROM OPENROWSET(
    BULK 'https://<storage-account>.dfs.core.windows.net/realtime/gold/shipment_summary/*.parquet',
    FORMAT = 'PARQUET'
)
WITH (
    total_orders BIGINT,
    revenue FLOAT,
    delayed_shipments BIGINT
) AS gold;

/*
Cost learning:
- In Synapse Studio, inspect query details / data processed.
- Compare SELECT * with the narrower query.
- Small POC files may make the difference tiny, but the principle matters:
  serverless query cost is related to data processed/scanned.
*/
