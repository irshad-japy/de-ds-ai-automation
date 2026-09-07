# Databricks notebook source

# COMMAND ----------
dbutils.widgets.text("bronze_path", "abfss://datalake@<storage>.dfs.core.windows.net/bronze/orders")
dbutils.widgets.text("silver_path", "abfss://datalake@<storage>.dfs.core.windows.net/silver/orders")
bronze_path = dbutils.widgets.get("bronze_path")
silver_path = dbutils.widgets.get("silver_path")

# COMMAND ----------
from pyspark.sql import functions as F
from pyspark.sql.window import Window

bronze = spark.read.format("delta").load(bronze_path)
window = Window.partitionBy("order_id").orderBy(F.col("ingestion_ts").desc())
clean = (
    bronze
    .withColumn("rn", F.row_number().over(window))
    .filter("rn = 1")
    .drop("rn")
    .withColumn("order_date", F.to_date("order_date"))
    .withColumn("quantity", F.col("quantity").cast("int"))
    .withColumn("unit_price", F.col("unit_price").cast("double"))
    .filter((F.col("quantity") > 0) & (F.col("unit_price") >= 0))
    .withColumn("line_amount", F.col("quantity") * F.col("unit_price"))
)
clean.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(silver_path)
print(f"Silver rows: {spark.read.format('delta').load(silver_path).count()}")
