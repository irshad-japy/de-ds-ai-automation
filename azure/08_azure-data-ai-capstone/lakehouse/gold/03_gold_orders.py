# Databricks notebook source

# COMMAND ----------
dbutils.widgets.text("silver_path", "abfss://datalake@<storage>.dfs.core.windows.net/silver/orders")
dbutils.widgets.text("gold_path", "abfss://datalake@<storage>.dfs.core.windows.net/gold/customer_metrics")
silver_path = dbutils.widgets.get("silver_path")
gold_path = dbutils.widgets.get("gold_path")

# COMMAND ----------
from pyspark.sql import functions as F

silver = spark.read.format("delta").load(silver_path)
gold = (
    silver.groupBy("customer_id")
    .agg(
        F.countDistinct("order_id").alias("total_orders"),
        F.sum("quantity").alias("total_units"),
        F.round(F.sum("line_amount"), 2).alias("total_revenue"),
    )
)
gold.write.format("delta").mode("overwrite").save(gold_path)
display(gold.orderBy(F.col("total_revenue").desc()))
