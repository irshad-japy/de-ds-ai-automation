# POC 08 — Event-Driven S3 -> SQS -> Lambda

## Objective

Create a decoupled intake path where an S3 object-created event enters SQS and Lambda processes the message.

## Why it matters

S3 notifications can be delivered more than once and are not guaranteed to be ordered. The consumer must therefore be retry-safe and idempotent.

## Flow

`S3 incoming/ -> SQS receipt-intake -> Lambda intake-handler -> downstream OCR step`

Attach a DLQ to the main SQS queue.

## Console steps

1. Create `receipt-intake-dlq`.
2. Create `receipt-intake`.
3. Configure redrive policy.
4. Allow S3 to send to the queue.
5. Configure S3 ObjectCreated event for only `incoming/`.
6. Create Lambda `receipt-intake-handler`.
7. Add SQS event source mapping.
8. Start with batch size 1 while learning.
9. Later enable partial batch failure behavior when batching.

## Lambda code

```python
import json, urllib.parse

def lambda_handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        # S3 may be direct in body; adapt if SNS/EventBridge wraps it.
        for s3record in body.get("Records", []):
            bucket = s3record["s3"]["bucket"]["name"]
            key = urllib.parse.unquote_plus(s3record["s3"]["object"]["key"])
            etag = s3record["s3"]["object"].get("eTag")
            sequencer = s3record["s3"]["object"].get("sequencer")
            print(json.dumps({
                "event": "receipt_received",
                "bucket": bucket,
                "key": key,
                "etag": etag,
                "sequencer": sequencer,
            }))
    return {"batchItemFailures": []}
```

## Verification

Upload one file and verify:
- S3 event sent,
- SQS receives/gets consumed,
- Lambda invocation occurs,
- log includes bucket/key,
- queue returns to zero visible messages.

## Failure test

Temporarily raise an exception for a known filename such as `poison.png`.
Observe:
- retry,
- receive count,
- eventual DLQ move based on redrive policy.

## Important configuration

Lambda timeout must not exceed SQS visibility timeout. For production, size the visibility timeout with sufficient margin and test long OCR-related processing.

## Success criteria

- event arrives exactly through the intended prefix,
- poison message reaches DLQ,
- successful messages are not repeatedly processed when partial-batch handling is configured,
- you understand duplicate-event risk.

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
