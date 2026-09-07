# Unity Catalog Notes

## Namespace

```text
catalog.schema.table
```

This project uses:

```text
azde_poc.bronze.orders
azde_poc.bronze.customers
azde_poc.silver.orders
azde_poc.silver.customers
azde_poc.gold.fact_orders
azde_poc.gold.dim_product
azde_poc.gold.dim_customer
azde_poc.quarantine.orders_invalid
azde_poc.quarantine.customers_invalid
```

## External storage objects

- Access Connector for Azure Databricks: Azure resource holding managed identity
- Storage credential: Unity Catalog object referring to the managed identity
- External location: Unity Catalog securable that combines the ADLS path and storage credential

## Recommended POC permissions

Use only your own account identity.

For the lab external location you need enough privileges to read/write files and create the quarantine external tables.

## Practice

```sql
SHOW EXTERNAL LOCATIONS;
SHOW GRANTS ON TABLE azde_poc.gold.fact_orders;
COMMENT ON TABLE azde_poc.gold.fact_orders IS 'POC-02 Gold fact table';
```

Use Catalog Explorer to view ownership and lineage.

## Security rule

Never place storage keys, SAS tokens, client secrets or Databricks tokens inside notebooks committed to GitHub.
