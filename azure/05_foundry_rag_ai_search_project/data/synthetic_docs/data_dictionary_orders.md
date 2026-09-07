---
title: Orders Data Dictionary
source: data_dictionary_orders.md
category: data_dictionary
effective_date: 2026-04-20
---
# Orders Data Dictionary

`order_id` is the unique string identifier for an order and is the primary business key in the curated orders dataset. `customer_id` identifies the synthetic customer. `order_timestamp_utc` stores the order creation time in UTC. `order_status` can be `created`, `paid`, `shipped`, `cancelled`, or `refunded`. `total_amount` stores the order total before any later refund event. `currency_code` uses a three-letter ISO-style currency code such as INR or USD.
