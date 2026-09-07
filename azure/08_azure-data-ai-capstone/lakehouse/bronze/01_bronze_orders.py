# Databricks notebook source
# Upload this file to Databricks and run it as a notebook.

# COMMAND ----------
dbutils.widgets.text("input_path", "abfss://datalake@<storage>.dfs.core.windows.net/raw/orders")
dbutils.widgets.text("bronze_path", "abfss://datalake@<storage>.dfs.core.windows.net/bronze/orders")
input_path = dbutils.widgets.get("input_path")
bronze_path = dbutils.widgets.get("bronze_path")

# COMMAND ----------
from pyspark.sql import functions as F

orders = spark.read.option("header", True).option("inferSchema", True).csv(input_path)
orders = orders.withColumn("ingestion_ts", F.current_timestamp()).withColumn("source_file", F.input_file_name())
orders.write.format("delta").mode("append").option("mergeSchema", "true").save(bronze_path)
print(f"Bronze rows: {spark.read.format('delta').load(bronze_path).count()}")
