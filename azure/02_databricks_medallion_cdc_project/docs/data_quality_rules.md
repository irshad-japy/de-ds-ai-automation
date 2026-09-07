# Data Quality Rules

## Orders

| Rule | Valid condition | Invalid action |
|---|---|---|
| Order key | `order_id` is not null/blank | quarantine |
| Quantity | parsed integer `> 0` | quarantine |
| Unit price | parsed decimal `>= 0` | quarantine |
| Order timestamp | parses as timestamp | quarantine |
| Updated timestamp | parses as timestamp | quarantine |
| Status | one of `CREATED`, `PROCESSING`, `SHIPPED`, `CANCELLED` | quarantine |

The Silver notebook concatenates failures into a readable `error_reason`.

## Customers

| Rule | Valid condition | Invalid action |
|---|---|---|
| Customer key | `customer_id` is not null/blank | quarantine |
| Name | `customer_name` is not null/blank | quarantine |
| Updated timestamp | parses as timestamp | quarantine |
| Email | blank/null allowed; otherwise contains `@` | quarantine |

## Deduplication

Orders are partitioned by `order_id`. Latest `updated_at` wins. `_ingest_ts` and `_source_file` are deterministic tie-breakers.

Customers use the same pattern by `customer_id`.

## Quarantine design

Invalid rows are written as Delta data under:

```text
abfss://poc02@<storage>.dfs.core.windows.net/quarantine/orders_invalid
abfss://poc02@<storage>.dfs.core.windows.net/quarantine/customers_invalid
```

They are registered as Unity Catalog external tables in `azde_poc.quarantine`.
