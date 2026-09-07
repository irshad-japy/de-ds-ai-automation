# Databricks notebook source
# MAGIC %md
# MAGIC # POC-02 - 03 Gold Fact/Dimensions, MERGE, SCD1 and SCD2

# COMMAND ----------
from delta.tables import DeltaTable
from pyspark.sql import functions as F

# COMMAND ----------
dbutils.widgets.text("catalog", "azde_poc")
catalog = dbutils.widgets.get("catalog").strip()

fact_table = f"{catalog}.gold.fact_orders"
product_table = f"{catalog}.gold.dim_product"
customer_table = f"{catalog}.gold.dim_customer"

# COMMAND ----------
# Create fact table with legacy Delta Change Data Feed enabled BEFORE data is merged.

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {fact_table} (
  order_id STRING,
  customer_id STRING,
  product_id STRING,
  quantity INT,
  unit_price DECIMAL(18,2),
  order_amount DECIMAL(20,2),
  status STRING,
  order_ts TIMESTAMP,
  updated_at TIMESTAMP,
  gold_updated_at TIMESTAMP
)
USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# COMMAND ----------
orders = spark.table(f"{catalog}.silver.orders")

fact_source = (
    orders.select(
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        (F.col("quantity") * F.col("unit_price")).cast("decimal(20,2)").alias("order_amount"),
        "status",
        "order_ts",
        "updated_at",
        F.current_timestamp().alias("gold_updated_at"),
    )
)

fact_delta = DeltaTable.forName(spark, fact_table)
(
    fact_delta.alias("t")
    .merge(fact_source.alias("s"), "t.order_id = s.order_id")
    .whenMatchedUpdateAll(condition="s.updated_at >= t.updated_at")
    .whenNotMatchedInsertAll()
    .execute()
)

# COMMAND ----------
# SCD Type 1 dim_product: only current product attributes are kept.

product_source = (
    orders.select("product_id", "product_name", "product_category", "updated_at")
    .groupBy("product_id")
    .agg(
        F.max_by("product_name", "updated_at").alias("product_name"),
        F.max_by("product_category", "updated_at").alias("product_category"),
        F.max("updated_at").alias("updated_at"),
    )
    .withColumn("dim_updated_at", F.current_timestamp())
)

if not spark.catalog.tableExists(product_table):
    product_source.write.format("delta").mode("overwrite").saveAsTable(product_table)
else:
    product_delta = DeltaTable.forName(spark, product_table)
    (
        product_delta.alias("t")
        .merge(product_source.alias("s"), "t.product_id = s.product_id")
        .whenMatchedUpdateAll(condition="s.updated_at >= t.updated_at")
        .whenNotMatchedInsertAll()
        .execute()
    )

# COMMAND ----------
# SCD Type 2 dim_customer: preserve history for tracked customer attributes.

customers = spark.table(f"{catalog}.silver.customers").select(
    "customer_id", "customer_name", "email", "city", "country", "updated_at"
)

if not spark.catalog.tableExists(customer_table):
    initial = (
        customers
        .withColumn(
            "customer_sk",
            F.sha2(F.concat_ws("||", "customer_id", F.col("updated_at").cast("string")), 256),
        )
        .withColumn("effective_from", F.col("updated_at"))
        .withColumn("effective_to", F.lit(None).cast("timestamp"))
        .withColumn("is_current", F.lit(True))
        .select(
            "customer_sk", "customer_id", "customer_name", "email", "city", "country",
            "effective_from", "effective_to", "is_current"
        )
    )
    initial.write.format("delta").mode("overwrite").saveAsTable(customer_table)
else:
    current = spark.table(customer_table).filter(F.col("is_current") == True).alias("t")
    src = customers.alias("s")

    joined = src.join(current, F.col("s.customer_id") == F.col("t.customer_id"), "left")

    same_attributes = (
        F.col("s.customer_name").eqNullSafe(F.col("t.customer_name"))
        & F.col("s.email").eqNullSafe(F.col("t.email"))
        & F.col("s.city").eqNullSafe(F.col("t.city"))
        & F.col("s.country").eqNullSafe(F.col("t.country"))
    )

    new_or_changed = (
        joined
        .filter(F.col("t.customer_id").isNull() | (~same_attributes))
        .select(
            F.col("s.customer_id").alias("customer_id"),
            F.col("s.customer_name").alias("customer_name"),
            F.col("s.email").alias("email"),
            F.col("s.city").alias("city"),
            F.col("s.country").alias("country"),
            F.col("s.updated_at").alias("updated_at"),
            F.col("t.customer_id").isNotNull().alias("was_existing"),
        )
    )

    changed_existing = new_or_changed.filter(F.col("was_existing") == True).select(
        "customer_id", "updated_at"
    )

    if changed_existing.limit(1).count() > 0:
        customer_delta = DeltaTable.forName(spark, customer_table)
        (
            customer_delta.alias("t")
            .merge(
                changed_existing.alias("s"),
                "t.customer_id = s.customer_id AND t.is_current = true",
            )
            .whenMatchedUpdate(
                set={
                    "effective_to": "s.updated_at",
                    "is_current": "false",
                }
            )
            .execute()
        )

    rows_to_insert = (
        new_or_changed
        .withColumn(
            "customer_sk",
            F.sha2(F.concat_ws("||", "customer_id", F.col("updated_at").cast("string")), 256),
        )
        .withColumn("effective_from", F.col("updated_at"))
        .withColumn("effective_to", F.lit(None).cast("timestamp"))
        .withColumn("is_current", F.lit(True))
        .select(
            "customer_sk", "customer_id", "customer_name", "email", "city", "country",
            "effective_from", "effective_to", "is_current"
        )
    )

    # Idempotence: do not append a history row if the same surrogate key already exists.
    existing_keys = spark.table(customer_table).select("customer_sk")
    rows_to_insert = rows_to_insert.join(existing_keys, "customer_sk", "left_anti")

    if rows_to_insert.limit(1).count() > 0:
        rows_to_insert.write.format("delta").mode("append").saveAsTable(customer_table)

# COMMAND ----------
print("Gold fact rows:", spark.table(fact_table).count())
print("Gold product rows:", spark.table(product_table).count())
print("Gold customer history rows:", spark.table(customer_table).count())

display(spark.table(fact_table).orderBy("order_id"))
display(spark.table(customer_table).orderBy("customer_id", "effective_from"))
