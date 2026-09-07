# Databricks notebook source
# MAGIC %md
# MAGIC # POC-02 - 02 Silver Quality, Standardization and Deduplication

# COMMAND ----------
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Disable ANSI strict parsing so malformed strings return NULL and route to quarantine
spark.conf.set("spark.sql.ansi.enabled", "false")

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

# COMMAND ----------
def merge_current_state(source_df, target_table: str, key: str):
    """Idempotent current-state upsert for this small POC."""
    if not spark.catalog.tableExists(target_table):
        source_df.write.format("delta").mode("overwrite").saveAsTable(target_table)
        print(f"Created {target_table}")
        return

    target = DeltaTable.forName(spark, target_table)
    (
        target.alias("t")
        .merge(source_df.alias("s"), f"t.{key} = s.{key}")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
    print(f"Merged into {target_table}")

# COMMAND ----------
# Orders: standardize types while keeping raw audit metadata.

orders_bronze = spark.table(f"{catalog}.bronze.orders")

orders_typed = (
    orders_bronze
    .withColumn("order_id_clean", F.when(F.length(F.trim(F.col("order_id"))) > 0, F.trim(F.col("order_id"))))
    .withColumn("customer_id_clean", F.trim(F.col("customer_id")))
    .withColumn("product_id_clean", F.trim(F.col("product_id")))
    .withColumn("quantity_typed", F.expr("try_cast(quantity as int)"))
    .withColumn("unit_price_typed", F.expr("try_cast(unit_price as decimal(18,2))"))
    .withColumn("order_ts_typed", F.expr("try_to_timestamp(order_ts)"))
    .withColumn("updated_at_typed", F.expr("try_to_timestamp(updated_at)"))
    .withColumn("status_clean", F.upper(F.trim(F.col("status"))))
)

allowed_statuses = ["CREATED", "PROCESSING", "SHIPPED", "CANCELLED"]

orders_checked = (
    orders_typed
    .withColumn(
        "error_reason",
        F.concat_ws(
            "; ",
            F.when(F.col("order_id_clean").isNull(), F.lit("order_id is null/blank")),
            F.when(F.col("quantity_typed").isNull() | (F.col("quantity_typed") <= 0), F.lit("quantity must be > 0")),
            F.when(F.col("unit_price_typed").isNull() | (F.col("unit_price_typed") < 0), F.lit("unit_price must be >= 0")),
            F.when(F.col("order_ts_typed").isNull(), F.lit("invalid order_ts")),
            F.when(F.col("updated_at_typed").isNull(), F.lit("invalid updated_at")),
            F.when(~F.col("status_clean").isin(allowed_statuses), F.lit("status is not allowed")),
        )
    )
)

invalid_orders = orders_checked.filter(F.length(F.col("error_reason")) > 0)
valid_orders = orders_checked.filter(F.length(F.col("error_reason")) == 0)

# COMMAND ----------
# Quarantine invalid records in an external Delta path under the UC external location.

orders_quarantine_path = f"{base}/quarantine/orders_invalid"
(
    invalid_orders
    .write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(orders_quarantine_path)
)

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {catalog}.quarantine.orders_invalid
USING DELTA
LOCATION '{orders_quarantine_path}'
""")

# COMMAND ----------
# Deterministic dedup: latest updated_at wins; audit fields break ties.

orders_window = Window.partitionBy("order_id_clean").orderBy(
    F.col("updated_at_typed").desc(),
    F.col("_ingest_ts").desc(),
    F.col("_source_file").desc(),
)

orders_dedup = (
    valid_orders
    .withColumn("_rn", F.row_number().over(orders_window))
    .filter(F.col("_rn") == 1)
    .select(
        F.col("order_id_clean").alias("order_id"),
        F.col("customer_id_clean").alias("customer_id"),
        F.col("product_id_clean").alias("product_id"),
        F.trim(F.col("product_name")).alias("product_name"),
        F.trim(F.col("product_category")).alias("product_category"),
        F.col("quantity_typed").alias("quantity"),
        F.col("unit_price_typed").alias("unit_price"),
        F.col("status_clean").alias("status"),
        F.col("order_ts_typed").alias("order_ts"),
        F.col("updated_at_typed").alias("updated_at"),
        "_ingest_ts",
        "_source_file",
        "_batch_id",
    )
)

merge_current_state(orders_dedup, f"{catalog}.silver.orders", "order_id")

# COMMAND ----------
# Customers quality + latest-record dedup.

customers_bronze = spark.table(f"{catalog}.bronze.customers")

customers_checked = (
    customers_bronze
    .withColumn("customer_id_clean", F.when(F.length(F.trim(F.col("customer_id"))) > 0, F.trim(F.col("customer_id"))))
    .withColumn("customer_name_clean", F.when(F.length(F.trim(F.col("customer_name"))) > 0, F.trim(F.col("customer_name"))))
    .withColumn("email_clean", F.lower(F.trim(F.col("email"))))
    .withColumn("updated_at_typed", F.expr("try_to_timestamp(updated_at)"))
    .withColumn(
        "error_reason",
        F.concat_ws(
            "; ",
            F.when(F.col("customer_id_clean").isNull(), F.lit("customer_id is null/blank")),
            F.when(F.col("customer_name_clean").isNull(), F.lit("customer_name is null/blank")),
            F.when(F.col("updated_at_typed").isNull(), F.lit("invalid updated_at")),
            F.when(
                F.col("email_clean").isNotNull() & (F.length(F.col("email_clean")) > 0) & (~F.col("email_clean").contains("@")),
                F.lit("email format is invalid"),
            ),
        )
    )
)

invalid_customers = customers_checked.filter(F.length(F.col("error_reason")) > 0)
valid_customers = customers_checked.filter(F.length(F.col("error_reason")) == 0)

customers_quarantine_path = f"{base}/quarantine/customers_invalid"
(
    invalid_customers
    .write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(customers_quarantine_path)
)

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {catalog}.quarantine.customers_invalid
USING DELTA
LOCATION '{customers_quarantine_path}'
""")

customers_window = Window.partitionBy("customer_id_clean").orderBy(
    F.col("updated_at_typed").desc(),
    F.col("_ingest_ts").desc(),
    F.col("_source_file").desc(),
)

customers_dedup = (
    valid_customers
    .withColumn("_rn", F.row_number().over(customers_window))
    .filter(F.col("_rn") == 1)
    .select(
        F.col("customer_id_clean").alias("customer_id"),
        F.col("customer_name_clean").alias("customer_name"),
        F.col("email_clean").alias("email"),
        F.trim(F.col("city")).alias("city"),
        F.trim(F.col("country")).alias("country"),
        F.col("updated_at_typed").alias("updated_at"),
        "_ingest_ts",
        "_source_file",
        "_batch_id",
    )
)

merge_current_state(customers_dedup, f"{catalog}.silver.customers", "customer_id")

# COMMAND ----------
print("Silver orders:", spark.table(f"{catalog}.silver.orders").count())
print("Silver customers:", spark.table(f"{catalog}.silver.customers").count())
print("Quarantined orders:", spark.table(f"{catalog}.quarantine.orders_invalid").count())
print("Quarantined customers:", spark.table(f"{catalog}.quarantine.customers_invalid").count())