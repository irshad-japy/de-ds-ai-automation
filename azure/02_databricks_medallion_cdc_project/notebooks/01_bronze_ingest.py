# Databricks notebook source
# MAGIC %md
# MAGIC # POC-02 - 01 Bronze Ingestion
# MAGIC Incrementally ingests new CSV files with Auto Loader and dedicated checkpoints.

# COMMAND ----------
from pyspark.sql import functions as F

# COMMAND ----------
dbutils.widgets.text("storage_account", "")
dbutils.widgets.text("container", "poc02")
dbutils.widgets.text("catalog", "azde_poc")
dbutils.widgets.text("batch_id", "manual")

storage_account = dbutils.widgets.get("storage_account").strip()
container = dbutils.widgets.get("container").strip()
catalog = dbutils.widgets.get("catalog").strip()
batch_id = dbutils.widgets.get("batch_id").strip() or "manual"

if not storage_account:
    raise ValueError("Set widget 'storage_account'.")

base = f"abfss://{container}@{storage_account}.dfs.core.windows.net"

# COMMAND ----------
def autoload_csv(source_subpath: str, table_name: str, stream_name: str):
    source_path = f"{base}/{source_subpath}"
    schema_location = f"{base}/schema/{stream_name}"
    checkpoint_location = f"{base}/checkpoints/{stream_name}"

    print(f"Loading {source_path} -> {table_name}")
    print(f"schema      : {schema_location}")
    print(f"checkpoint  : {checkpoint_location}")

    df = (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        # Keep Bronze source values as strings. Silver owns business typing.
        .option("cloudFiles.inferColumnTypes", "false")
        .option("cloudFiles.schemaLocation", schema_location)
        # Intentional schema-evolution lab behavior.
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .option("rescuedDataColumn", "_rescued_data")
        .load(source_path)
        .withColumn("_ingest_ts", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_batch_id", F.lit(batch_id))
    )

    query = (
        df.writeStream
        .option("checkpointLocation", checkpoint_location)
        .option("mergeSchema", "true")
        .trigger(availableNow=True)
        .toTable(table_name)
    )
    query.awaitTermination()
    print(f"Completed {stream_name}")

# COMMAND ----------
autoload_csv(
    source_subpath="raw/orders",
    table_name=f"{catalog}.bronze.orders",
    stream_name="bronze_orders",
)

# COMMAND ----------
autoload_csv(
    source_subpath="raw/customers",
    table_name=f"{catalog}.bronze.customers",
    stream_name="bronze_customers",
)

# COMMAND ----------
print("Bronze order count:", spark.table(f"{catalog}.bronze.orders").count())
print("Bronze customer count:", spark.table(f"{catalog}.bronze.customers").count())

display(
    spark.table(f"{catalog}.bronze.orders")
    .groupBy("_source_file", "_batch_id")
    .count()
    .orderBy("_source_file")
)
