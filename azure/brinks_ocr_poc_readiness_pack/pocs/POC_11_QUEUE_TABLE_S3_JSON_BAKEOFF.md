# POC 11 — Queue vs Table vs S3 JSON Handoff Bakeoff

## Objective

Turn the kickoff's unresolved "queue/table/json" question into a small evidence-based comparison.

## Build three mini flows

### A. SQS payload
Normalize receipt -> put full canonical JSON on SQS -> mock consumer reads it.

### B. SQS pointer + S3 JSON
Normalize receipt -> save JSON to S3 -> send compact SQS pointer -> mock consumer loads S3 object.

### C. State table + pointer/event
Normalize receipt -> save immutable JSON to S3 -> update DynamoDB state -> send event/queue pointer.

## Measure

- payload size
- end-to-end latency
- replay ease
- duplicate behavior
- operational visibility
- consumer complexity
- auditability
- retention behavior
- IAM/network complexity

## Example pointer message

```json
{
  "event_type": "receipt.normalized.v1",
  "document_id": "doc-123",
  "correlation_id": "corr-123",
  "payload": {
    "bucket": "replace-me",
    "key": "normalized/doc-123.json"
  }
}
```

## Success criteria

Produce a one-page recommendation containing:
- chosen pattern,
- rejected alternatives,
- assumptions,
- constraints,
- failure/replay behavior,
- ownership boundary.

Do not finalize it until MuleSoft/iCash constraints are known.

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
