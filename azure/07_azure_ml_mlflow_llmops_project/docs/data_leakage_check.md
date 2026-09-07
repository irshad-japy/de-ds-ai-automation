# Data leakage review

## Approved prediction-time features

The model uses only the source POC features: `origin_region`, `destination_region`, `carrier`, `distance_km`, `order_hour`, `weekday`, `priority`, and `historical_delay_rate`.

These values are assumed to be known at or before the prediction decision. The label is `is_delayed`.

## Explicitly excluded examples

Do **not** add fields that become known only after the shipment outcome, such as actual delivery timestamp, actual delay minutes, late-delivery reason, compensation/refund amount, post-delivery customer complaint, or a status that directly says the shipment was delayed.

## Split policy

This educational POC uses a deterministic stratified train/validation split. For a real shipment system, prefer a time-based holdout (train on older shipments, validate on newer shipments) when operational chronology matters.

## Result

Leakage review status: **PASS for the defined synthetic feature list**, subject to the assumption that `historical_delay_rate` is computed only from records available before each prediction time.
