# Schema Evolution Exercise

## Goal

Demonstrate an additive source schema change without blindly allowing source drift to alter every business table.

## Phase 1

`orders_batch_001.csv` does not contain `sales_channel`.

## Phase 2

`orders_batch_002_schema_evolution.csv` adds the nullable column:

```text
sales_channel
```

Example values:

```text
WEB
MOBILE
PARTNER
```

## Auto Loader behavior used

Bronze sets:

```python
.option("cloudFiles.schemaLocation", "...")
.option("cloudFiles.schemaEvolutionMode", "addNewColumns")
.option("rescuedDataColumn", "_rescued_data")
```

With `addNewColumns`, a newly discovered column can stop the stream after the schema location is updated. Rerunning the stream uses the updated schema.

## Controlled downstream behavior

Bronze accepts the additive source change.

Silver deliberately selects an approved column contract and therefore does not automatically promote `sales_channel`.

Gold also remains unchanged until the business decides that the new field is needed.

This demonstrates why unrestricted schema drift is risky: a harmless source field addition should not unexpectedly change reporting contracts, downstream schemas, security expectations or BI models.

## Verify

```sql
DESCRIBE TABLE azde_poc.bronze.orders;

SELECT order_id, sales_channel, _batch_id
FROM azde_poc.bronze.orders
WHERE _batch_id = 'phase2';
```
