# Confidence and validation rules

This POC follows the source POC requirement to validate critical invoice fields and route low-confidence/invalid documents to quarantine.

## Critical confidence fields

Default threshold: **0.70** (configurable with `CRITICAL_CONFIDENCE_THRESHOLD`).

Critical fields:

- invoice number
- invoice date
- supplier name
- subtotal
- total

If Document Intelligence returns a confidence score below the threshold for any critical field, the invoice is routed to `documents/failed/`.

## Financial reconciliation

Default absolute tolerance: **0.05** (configurable with `AMOUNT_TOLERANCE`).

1. Sum of extracted line amounts should approximately equal subtotal.
2. `subtotal + tax` should approximately equal total.
3. Total must be greater than zero.
4. Invoice number is mandatory.

## Production note

A real production solution usually varies thresholds by field/document type and may send uncertain documents to a human review queue instead of treating every low-confidence result as a hard failure.
