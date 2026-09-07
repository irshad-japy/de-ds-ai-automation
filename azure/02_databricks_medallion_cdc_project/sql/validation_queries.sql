-- POC-02 validation queries
-- Run section by section after the corresponding notebook.

-- 1) Namespace
SHOW CATALOGS;
SHOW SCHEMAS IN azde_poc;
SHOW EXTERNAL LOCATIONS;

-- 2) Bronze counts by source file and batch
SELECT _source_file, _batch_id, COUNT(*) AS row_count
FROM azde_poc.bronze.orders
GROUP BY _source_file, _batch_id
ORDER BY _source_file;

SELECT _source_file, _batch_id, COUNT(*) AS row_count
FROM azde_poc.bronze.customers
GROUP BY _source_file, _batch_id
ORDER BY _source_file;

-- 3) Schema evolution: sales_channel should appear after phase 2
DESCRIBE TABLE azde_poc.bronze.orders;
SELECT order_id, sales_channel, _batch_id
FROM azde_poc.bronze.orders
WHERE _batch_id = 'phase2'
ORDER BY order_id;

-- 4) Quarantine
SELECT order_id, quantity, unit_price, status, order_ts, updated_at, error_reason
FROM azde_poc.quarantine.orders_invalid
ORDER BY _source_file;

SELECT customer_id, customer_name, email, updated_at, error_reason
FROM azde_poc.quarantine.customers_invalid;

-- 5) Silver duplicates should return no rows
SELECT order_id, COUNT(*) AS c
FROM azde_poc.silver.orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 6) Specific duplicate resolution
SELECT order_id, status, updated_at, _source_file
FROM azde_poc.silver.orders
WHERE order_id = 'O1002';

-- 7) Gold fact
SELECT order_id, customer_id, product_id, quantity, unit_price, order_amount, status, updated_at
FROM azde_poc.gold.fact_orders
ORDER BY order_id;

-- 8) SCD1 product current state
SELECT *
FROM azde_poc.gold.dim_product
ORDER BY product_id;

-- 9) SCD2 customer history
SELECT customer_id, customer_name, city, country,
       effective_from, effective_to, is_current
FROM azde_poc.gold.dim_customer
ORDER BY customer_id, effective_from;

-- Exactly one current row per customer; expected no rows.
SELECT customer_id,
       SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_rows
FROM azde_poc.gold.dim_customer
GROUP BY customer_id
HAVING current_rows <> 1;

-- Customer C002 should show history after phase 2.
SELECT customer_id, city, effective_from, effective_to, is_current
FROM azde_poc.gold.dim_customer
WHERE customer_id = 'C002'
ORDER BY effective_from;

-- 10) MERGE/CDF table history
DESCRIBE HISTORY azde_poc.gold.fact_orders;
SHOW TBLPROPERTIES azde_poc.gold.fact_orders;

-- 11) Batch CDF
SELECT order_id, status, _change_type, _commit_version, _commit_timestamp
FROM table_changes('azde_poc.gold.fact_orders', 0)
ORDER BY _commit_version, order_id, _change_type;

SELECT _change_type, COUNT(*) AS change_count
FROM table_changes('azde_poc.gold.fact_orders', 0)
GROUP BY _change_type
ORDER BY _change_type;

-- 12) Persisted CDF consumer output
SELECT _change_type, COUNT(*) AS c
FROM azde_poc.gold.fact_orders_changes_audit
GROUP BY _change_type
ORDER BY _change_type;

-- 13) Delta metadata
DESCRIBE DETAIL azde_poc.gold.fact_orders;

-- 14) Query plan example
EXPLAIN FORMATTED
SELECT f.order_id, f.order_amount, c.customer_name
FROM azde_poc.gold.fact_orders f
JOIN azde_poc.gold.dim_customer c
  ON f.customer_id = c.customer_id
 AND c.is_current = true
WHERE f.order_amount >= 20;

-- 15) Unity Catalog permissions
SHOW GRANTS ON TABLE azde_poc.gold.fact_orders;
