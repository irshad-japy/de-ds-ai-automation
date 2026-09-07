# Databricks notebook source
# MAGIC %md
# MAGIC # POC-02 - 04 Change Data Feed Consumer
# MAGIC Uses legacy table CDF enabled on `gold.fact_orders` and persists consumed changes.

# COMMAND ----------
from pyspark.sql import functions as F

# COMMAND ----------
dbutils.widgets.text("storage_account", "")
dbutils.widgets.text("container", "poc02")
dbutils.widgets.text("catalog", "azde_poc")

storage_account = dbutils.widgets.get("storage_account").strip()
container = dbutils.widgets.get("container").strip()
catalog = dbutils.widgets.get("catalog").strip()

if not storage_account:
    raise ValueError("Set widget 'storage_account'.")

base = f"abfss://{container}@{storage_account}.dfs.core.windows.net"
source_table = f"{catalog}.gold.fact_orders"
audit_table = f"{catalog}.gold.fact_orders_changes_audit"
checkpoint = f"{base}/checkpoints/cdf/fact_orders_changes_audit"

# COMMAND ----------
# Inspect table history first so you understand available versions.

display(spark.sql(f"DESCRIBE HISTORY {source_table}"))

# COMMAND ----------
# Batch CDF inspection. CDF was enabled when the table was created by 03_gold_dimensions.py.

cdf_batch = (
    spark.read
    .option("readChangeFeed", "true")
    .option("startingVersion", 0)
    .table(source_table)
)

display(cdf_batch.orderBy("_commit_version", "order_id", "_change_type"))

# COMMAND ----------
# Incremental CDF consumer. The checkpoint prevents duplicate consumption on rerun.

cdf_stream = (
    spark.readStream
    .option("readChangeFeed", "true")
    .option("startingVersion", 0)
    .table(source_table)
    .withColumn("_consumer_ingest_ts", F.current_timestamp())
)

query = (
    cdf_stream.writeStream
    .option("checkpointLocation", checkpoint)
    .trigger(availableNow=True)
    .toTable(audit_table)
)
query.awaitTermination()

# COMMAND ----------
print("CDF audit row count:", spark.table(audit_table).count())
display(
    spark.table(audit_table)
    .groupBy("_change_type")
    .count()
    .orderBy("_change_type")
)
