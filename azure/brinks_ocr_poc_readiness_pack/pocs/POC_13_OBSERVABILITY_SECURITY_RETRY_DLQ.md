# POC 13 — Observability, Security, Retry, and DLQ

## Objective

Make the pipeline supportable rather than merely functional.

## Structured log example

```python
import json, logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_event(name, **kwargs):
    safe = {k: v for k, v in kwargs.items() if k not in {"raw_text", "receipt_payload"}}
    logger.info(json.dumps({"event": name, **safe}))
```

Recommended log identifiers:
- correlation_id
- document_id
- stage
- status
- attempt
- latency_ms
- error_code
- receipt_format_id (if non-sensitive/approved)

Avoid high-cardinality custom metric dimensions such as request/document IDs.

## Metrics

- documents_received
- ocr_succeeded
- ocr_failed
- validation_review
- handoff_succeeded
- handoff_failed
- dlq_depth
- processing_latency_ms
- extraction_latency_ms
- low_confidence_field_count

## Alarms

Prototype alarms for:
- DLQ > 0
- Lambda errors
- throttles
- age of oldest SQS message
- no successful processing for an abnormal interval
- unusual validation failure rate

## Retry design

Classify failures:
- retryable infrastructure/service error
- throttling
- downstream 5xx/429
- non-retryable invalid document
- non-retryable schema/business validation

Use exponential backoff/jitter where appropriate; avoid hot-loop retries.

## Security checklist

- no public S3
- least privilege
- encryption requirements confirmed
- secrets in Secrets Manager/Parameter Store where approved, not code
- CloudTrail/audit requirements confirmed
- sensitive payload excluded from logs
- resource policies scoped
- non-production and production separated
- dependency/package scanning per project standards

## DLQ replay drill

1. force a poison receipt.
2. observe DLQ.
3. diagnose root cause.
4. fix configuration/code.
5. replay only the intended message.
6. confirm idempotency.
7. record runbook steps.

## Success criteria

An engineer can find a failed document by correlation/document ID, understand its stage, fix it, and safely replay it.

## Safety before you begin

Use a sandbox/non-production AWS account and synthetic or approved redacted receipts. Never upload real Brinks/customer/bank receipt data to a personal account. Do not copy production credentials into source code.

## Local prerequisites

- Python 3.11+ (3.12 is fine for these examples)
- AWS CLI v2
- an authorized AWS account/profile
- `boto3`
- `python-dotenv`
- `pytest` for test exercises

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install boto3 python-dotenv pytest
aws --version
aws sts get-caller-identity
```

Set a profile if needed:

```powershell
$env:AWS_PROFILE="brinks-poc"
$env:AWS_REGION="us-east-1"
```

Replace all sample names and regions with values approved for your account.

## Evidence to capture

For each POC save:
- command used,
- input document ID,
- CloudWatch request/correlation ID where relevant,
- sanitized output JSON,
- pass/fail result,
- issue and fix,
- measured latency,
- measured confidence/accuracy where applicable.

## Cleanup rule

Delete only resources created by your POC. In a shared Brinks account, never delete a resource unless the owner confirms it is disposable.
