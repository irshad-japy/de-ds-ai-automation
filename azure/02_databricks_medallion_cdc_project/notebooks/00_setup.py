# Databricks notebook source
# MAGIC %md
# MAGIC # POC-02 - 00 Setup
# MAGIC Creates the Unity Catalog logical structure and validates the ADLS path.

# COMMAND ----------

dbutils.widgets.text("storage_account", "")
dbutils.widgets.text("container", "poc02")
dbutils.widgets.text("catalog", "azde_poc")

storage_account = dbutils.widgets.get("storage_account").strip()
container = dbutils.widgets.get("container").strip()
catalog = dbutils.widgets.get("catalog").strip()

if not storage_account:
    raise ValueError("Set widget 'storage_account' to your ADLS Gen2 storage account name.")

base_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net"
orders_path = f"{base_path}/raw/orders"
customers_path = f"{base_path}/raw/customers"
checkpoints_path = f"{base_path}/checkpoints"
schema_path = f"{base_path}/schema"
quarantine_path = f"{base_path}/quarantine"

print("POC-02 configuration")
print(f"catalog       = {catalog}")
print(f"base_path     = {base_path}")
print(f"orders_path   = {orders_path}")
print(f"customers_path= {customers_path}")

# COMMAND ----------
# Create logical Medallion schemas.
# You need CREATE CATALOG permission for a brand-new catalog.

managed_catalog_path = f"{base_path}/managed/{catalog}"
spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog} MANAGED LOCATION '{managed_catalog_path}'")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.bronze")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.silver")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.gold")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.quarantine")

# COMMAND ----------
# Validate that the current Databricks identity can see the landing directories.
# Phase-1 files must be uploaded before these directories contain files.

print("Orders directory:")
for item in dbutils.fs.ls(orders_path):
    print(item.path)

print("Customers directory:")
for item in dbutils.fs.ls(customers_path):
    print(item.path)

# COMMAND ----------
print("Schemas created/verified:")
display(spark.sql(f"SHOW SCHEMAS IN {catalog}"))
