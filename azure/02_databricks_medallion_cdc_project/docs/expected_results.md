# Expected Results

These exact counts assume you use the provided sample files unchanged.

## After Phase 1 Bronze

| Object | Expected rows |
|---|---:|
| `bronze.orders` | 9 |
| `bronze.customers` | 4 |

Re-running Bronze without new files should keep the same counts.

## After Phase 1 Silver

The orders file contains five intentionally invalid rows and one duplicate business key.

| Object | Expected rows |
|---|---:|
| `silver.orders` | 3 |
| `quarantine.orders_invalid` | 5 |
| `silver.customers` | 3 |
| `quarantine.customers_invalid` | 1 |

`O1002` should appear once in Silver with status `SHIPPED` because the later `updated_at` wins.

## After Phase 1 Gold

| Object | Expected rows |
|---|---:|
| `gold.fact_orders` | 3 |
| `gold.dim_customer` history rows | 3 |
| current customers | 3 |

## After Phase 2 Bronze

Phase 2 adds three order rows and two customer rows.

| Object | Expected rows |
|---|---:|
| `bronze.orders` | 12 |
| `bronze.customers` | 6 |

The Bronze orders schema should now include nullable `sales_channel`.

## After Phase 2 Silver

| Object | Expected rows |
|---|---:|
| `silver.orders` | 5 |
| `silver.customers` | 4 |

The Silver order for `O1001` should have status `SHIPPED`.

## After Phase 2 Gold

| Object | Expected rows |
|---|---:|
| `gold.fact_orders` | 5 |
| `gold.dim_customer` history rows | 5 |
| current customer rows | 4 |

For `C002`, expect two history rows:

1. `Mumbai`, `is_current=false`
2. `Bengaluru`, `is_current=true`

## CDF expectations

The fact table is created with CDF enabled before data is merged. With the provided data, the full batch CDF history should include:

- five inserts in total across the two phases
- one `update_preimage` for `O1001`
- one `update_postimage` for `O1001`

The persisted CDF audit table uses a checkpoint. After its first successful run, rerunning it without another fact-table change should not add duplicate events.

Exact commit version numbers/timestamps can vary, so validate change types and business keys rather than assuming a particular version number.
