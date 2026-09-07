# POC 09 — Asynchronous Textract with SNS/SQS

## Objective

Practice the asynchronous Start/Get model used for documents that should not be handled as a single synchronous call.

## Why it matters

Textract asynchronous operations return a JobId and publish completion to SNS. Polling Get APIs aggressively is not the preferred completion mechanism.

## Flow

```text
S3 document
  -> Lambda/start worker
  -> StartExpenseAnalysis
  -> JobId/state
  -> Textract
  -> SNS completion
  -> SQS completion queue
  -> result worker
  -> GetExpenseAnalysis (paginate)
  -> raw JSON
  -> normalize
```

## AWS resources

- S3 input bucket
- SNS topic (same Region as required by Textract async setup)
- SQS completion queue subscribed to SNS
- IAM service role permitting Textract to publish to the topic
- start worker
- result worker

## Start sketch

```python
resp = textract.start_expense_analysis(
    DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
    NotificationChannel={
        "SNSTopicArn": os.environ["TEXTRACT_SNS_ARN"],
        "RoleArn": os.environ["TEXTRACT_SNS_ROLE_ARN"],
    },
    JobTag=document_id,
)
job_id = resp["JobId"]
```

## Result pagination sketch

```python
pages = []
token = None
while True:
    kwargs = {"JobId": job_id}
    if token:
        kwargs["NextToken"] = token
    r = textract.get_expense_analysis(**kwargs)
    pages.extend(r.get("ExpenseDocuments", []))
    token = r.get("NextToken")
    if not token:
        break
```

## Verification

- start call returns JobId.
- completion message arrives through SNS -> SQS.
- result worker calls Get only after `SUCCEEDED`.
- pagination is handled.
- failed job status is recorded and routed correctly.

## Negative tests

- wrong SNS role
- S3 object removed before processing
- invalid document
- result worker receives duplicate completion
- processing status = FAILED

## Success criteria

You can explain why JobId, notification, persistence, and idempotency must work together.

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
