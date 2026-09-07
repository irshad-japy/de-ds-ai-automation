# POC 10 — Idempotency and Processing State

## Objective

Make duplicate S3/SQS events and retries safe.

## Why it matters

At-least-once event delivery means the same logical receipt can reach your consumer more than once. Calling downstream systems twice can create duplicate side effects.

## POC table

DynamoDB table:
- partition key: `document_id`
- attributes: status, source_key, source_etag, textract_job_id, attempt_count, updated_at, payload_key, error

Choose the real key only after duplicate semantics are defined.

## Conditional write

```python
import boto3
ddb = boto3.resource("dynamodb")
table = ddb.Table("receipt-processing-poc")

def claim(document_id, source_key, source_etag):
    return table.put_item(
        Item={
            "document_id": document_id,
            "status": "RECEIVED",
            "source_key": source_key,
            "source_etag": source_etag,
        },
        ConditionExpression="attribute_not_exists(document_id)"
    )
```

If the conditional write fails because the item already exists, inspect its state rather than blindly processing again.

## Suggested state machine

```text
RECEIVED
-> OCR_STARTED
-> OCR_COMPLETE
-> NORMALIZED
-> VALIDATED
-> HANDED_OFF

alternate:
-> REVIEW
-> FAILED_RETRYABLE
-> FAILED_FINAL
```

## Tests

1. same SQS message twice
2. same S3 object event twice
3. Lambda crash after Textract start
4. crash after normalized JSON write
5. duplicate MuleSoft handoff attempt
6. stale in-progress record

## Success criteria

- duplicate receipt event does not create duplicate side effect,
- resumed processing can determine the last safe stage,
- state transitions are observable,
- immutable raw/normalized payloads remain traceable.

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
