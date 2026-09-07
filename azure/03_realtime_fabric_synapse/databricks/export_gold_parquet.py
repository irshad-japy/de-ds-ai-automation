# Databricks notebook source
# Create a tiny Gold aggregate and publish it as Parquet.
# The Parquet output is intentionally easy to query from Synapse serverless SQL.

from pyspark.sql import functions as F

SILVER_PATH = "abfss://realtime@<storage-account>.dfs.core.windows.net/delta/silver/shipment_events"
GOLD_PARQUET_PATH = "abfss://realtime@<storage-account>.dfs.core.windows.net/gold/shipment_summary"

silver = spark.read.format("delta").load(SILVER_PATH)

gold = (
    silver.groupBy("region")
    .agg(
        F.countDistinct("order_id").alias("total_orders"),
        F.round(F.sum("revenue"), 2).alias("revenue"),
        F.sum(F.when(F.col("event_type") == "DELAYED", 1).otherwise(0)).alias("delayed_shipments"),
        F.round(F.avg("fulfillment_minutes"), 2).alias("avg_fulfillment_minutes"),
        F.max("event_ts").alias("last_event_ts"),
    )
)

display(gold)

(
    gold.coalesce(1)
    .write
    .mode("overwrite")
    .parquet(GOLD_PARQUET_PATH)
)

print("Gold Parquet written to:", GOLD_PARQUET_PATH)
