# Databricks notebook source
# MAGIC %md
# MAGIC # POC-02 - 05 Performance and Governance Inspection
# MAGIC This tiny POC is for concepts, not benchmark numbers.

# COMMAND ----------
dbutils.widgets.text("catalog", "azde_poc")
catalog = dbutils.widgets.get("catalog").strip()

fact = f"{catalog}.gold.fact_orders"
dim_customer = f"{catalog}.gold.dim_customer"

# COMMAND ----------
# Spark partition count for the in-memory DataFrame representation.

fact_df = spark.table(fact)
print("fact_orders Spark partitions:", fact_df.rdd.getNumPartitions())

# COMMAND ----------
# Query plan: inspect joins, scans, exchanges/shuffles and filters.

query_df = spark.sql(f"""
SELECT f.order_id, f.order_amount, c.customer_name, c.city
FROM {fact} f
JOIN {dim_customer} c
  ON f.customer_id = c.customer_id
 AND c.is_current = true
WHERE f.order_amount >= 20
""")

query_df.explain("formatted")
display(query_df)

# COMMAND ----------
# Delta metadata: number of files, total size, table format, etc.

display(spark.sql(f"DESCRIBE DETAIL {fact}"))
display(spark.sql(f"DESCRIBE HISTORY {fact}"))

# COMMAND ----------
# Unity Catalog governance inspection.

display(spark.sql(f"SHOW GRANTS ON TABLE {fact}"))

spark.sql(f"""
COMMENT ON TABLE {fact}
IS 'POC-02 business-ready order fact table with Delta Change Data Feed enabled'
""")

print("Use Catalog Explorer to inspect ownership, permissions and lineage.")
