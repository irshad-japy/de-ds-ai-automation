# 02 — Architecture Decision Questions and Handoff Bakeoff

## Why this file exists

The kickoff explicitly leaves the downstream mechanism open: queue/table/JSON was still to be finalized. Use this as a decision aid, not as a final architecture.

## Candidate patterns

### Pattern A — SQS message contains canonical payload
Good when:
- payload is small,
- MuleSoft can consume SQS through an approved connector/pattern,
- decoupling and retry buffering are important.

Risks:
- message-size constraints,
- duplicate delivery,
- visibility-timeout/retry semantics,
- sensitive content in messages may increase handling concerns.

### Pattern B — SQS message contains a pointer to S3 JSON
Good when:
- OCR JSON can be large,
- immutable payload/archive is desirable,
- message should contain only identifiers and object URI/key.

Typical message:
```json
{
  "event_type": "receipt.normalized.v1",
  "document_id": "doc-123",
  "correlation_id": "corr-123",
  "payload_bucket": "REPLACE_ME",
  "payload_key": "normalized/doc-123.json"
}
```

### Pattern C — DynamoDB/state table + event pointer
Good when:
- state transitions must be queryable,
- idempotency and processing history are important,
- downstream consumers need status lookup.

Do not use DynamoDB as a substitute for an immutable raw-result archive.

### Pattern D — API call to MuleSoft
Good when:
- MuleSoft exposes a stable authenticated endpoint,
- immediate acknowledgement is required.

Risks:
- tighter coupling,
- retry ownership,
- backpressure,
- MuleSoft outage can directly affect AWS pipeline unless buffered.

## Decision criteria to confirm

Score each 1–5:
- payload size
- throughput
- ordering need
- persistence/retention
- auditability
- replay
- duplicate tolerance
- consumer capability
- security controls
- operations ownership
- latency
- cost
- schema evolution
- cross-account/network constraints

## Recommendation for POC testing

Use S3 JSON as the durable payload during POCs and put only a compact pointer/event into SQS. This is a recommendation for experimentation because it makes replay/debugging easy; it is not a statement of the final Brinks design.
