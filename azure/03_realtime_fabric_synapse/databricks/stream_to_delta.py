# Databricks notebook source
# POC-03: Azure Event Hubs -> Databricks Structured Streaming -> Delta Lake (Serverless Compatible)

import os

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, DoubleType
)

# COMMAND ----------
# 1) Configuration & Unity Catalog Volume Setup

# Ensure the Unity Catalog managed volume exists
spark.sql("CREATE VOLUME IF NOT EXISTS dbw_logistics_poc.default.realtime")

# Event Hub settings
EVENT_HUB_NAMESPACE = os.environ.get("EVENT_HUB_NAMESPACE", "dbw-logistics-poc")
EVENT_HUB_NAME = os.environ.get("EVENT_HUB_NAME", "shipment-events")
EVENT_HUB_CONNECTION_STRING = os.environ.get("EVENT_HUB_CONNECTION_STRING", "endpoint")

# Volume storage paths (uses /v2/ checkpoints to avoid skipping previously sent events)
VOLUME_BASE = "/Volumes/dbw_logistics_poc/default/realtime"
BRONZE_PATH = f"{VOLUME_BASE}/delta/bronze/shipment_events"
BRONZE_CHECKPOINT = f"{VOLUME_BASE}/checkpoints/v3/bronze/shipment_events"
SILVER_CHECKPOINT = f"{VOLUME_BASE}/checkpoints/v3/silver/shipment_events"

SILVER_PATH = f"{VOLUME_BASE}/delta/silver/shipment_events"

# Kafka SASL JAAS config for Azure Event Hubs
JAAS = (
    'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required '
    f'username="$ConnectionString" password="{EVENT_HUB_CONNECTION_STRING}";'
)

# Streaming options (startingOffsets=earliest consumes all 200 backlog events)
kafka_options = {
    "kafka.bootstrap.servers": f"{EVENT_HUB_NAMESPACE}.servicebus.windows.net:9093",
    "subscribe": EVENT_HUB_NAME,
    "kafka.sasl.mechanism": "PLAIN",
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.jaas.config": JAAS,
    "startingOffsets": "earliest",
    "failOnDataLoss": "false",
}

# COMMAND ----------
# 2) Define JSON Schema for Telemetry Events

event_schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("order_id", LongType(), False),
    StructField("event_type", StringType(), False),
    StructField("event_ts", StringType(), False),
    StructField("region", StringType(), False),
    StructField("revenue", DoubleType(), True),
    StructField("fulfillment_minutes", LongType(), True),
    StructField("producer_seq", LongType(), True),
])

# COMMAND ----------
# 3) Bronze Layer: Read Stream & Persist Raw Payload

raw = (
    spark.readStream
    .format("kafka")
    .options(**kafka_options)
    .load()
)

bronze = (
    raw.select(
        F.col("key").cast("string").alias("kafka_key"),
        F.col("value").cast("string").alias("json_body"),
        F.col("topic"),
        F.col("partition"),
        F.col("offset"),
        F.col("timestamp").alias("eventhub_enqueued_ts"),
    )
    .withColumn("ingested_at", F.current_timestamp())
)

bronze_query = (
    bronze.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", BRONZE_CHECKPOINT)
    .trigger(availableNow=True)
    .start(BRONZE_PATH)
)

print(f"Bronze stream started (ID: {bronze_query.id}). Waiting for batch to complete...")
bronze_query.awaitTermination(60)
print("Bronze raw events successfully written.")

# COMMAND ----------
# 4) Silver Layer: Parse JSON, Watermark, Deduplicate & Persist

parsed = (
    bronze
    .withColumn("j", F.from_json("json_body", event_schema))
    .select(
        "j.*",
        "partition",
        "offset",
        "eventhub_enqueued_ts",
        "ingested_at",
    )
    .withColumn("event_ts", F.to_timestamp("event_ts"))
    .filter(F.col("event_id").isNotNull())
)

# Apply 10-minute watermark and deduplicate on event_id
silver = (
    parsed
    .withWatermark("event_ts", "10 minutes")
    .dropDuplicatesWithinWatermark(["event_id"])
)

silver_query = (
    silver.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", SILVER_CHECKPOINT)
    .trigger(availableNow=True)
    .start(SILVER_PATH)
)

print(f"Silver stream started (ID: {silver_query.id}). Waiting for batch to complete...")
silver_query.awaitTermination(60)
print("Silver transformation completed successfully!")

# COMMAND ----------
# 5) Query and Inspect Silver Delta Table

df_silver = spark.read.format("delta").load(SILVER_PATH)
print(f"Total rows in Silver Delta table: {df_silver.count()}")
display(df_silver)