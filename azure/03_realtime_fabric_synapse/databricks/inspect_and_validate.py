# Databricks notebook source
from pyspark.sql import functions as F

SILVER_PATH = "/Volumes/dbw_logistics_poc/default/realtime/delta/silver/shipment_events"

df = spark.read.format("delta").load(SILVER_PATH)

print("Silver rows:", df.count())
print("Distinct event_id:", df.select("event_id").distinct().count())

display(
    df.groupBy("event_type")
      .count()
      .orderBy(F.desc("count"))
)

display(
    df.groupBy("region")
      .agg(
          F.count("*").alias("events"),
          F.sum("revenue").alias("revenue"),
          F.avg("fulfillment_minutes").alias("avg_fulfillment_minutes"),
      )
      .orderBy("region")
)

# Dedup test: these two values should be equal after Silver processing.
row_count = df.count()
distinct_count = df.select("event_id").distinct().count()
assert row_count == distinct_count, (
    f"Dedup failed: row_count={row_count}, distinct_event_id={distinct_count}"
)

print("PASS: Silver contains no duplicate event_id values.")
