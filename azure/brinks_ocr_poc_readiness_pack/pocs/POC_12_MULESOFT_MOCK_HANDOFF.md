# POC 12 — MuleSoft Handoff Contract with a Mock Consumer/API

## Objective

Practice the AWS-to-MuleSoft boundary without inventing the real endpoint or contract.

## Why it matters

The kickoff says MuleSoft will take the OCR output and send it to iCash, but the exact integration mechanism is not provided.

## Option A — local mock HTTP endpoint

Install:

```powershell
pip install fastapi uvicorn requests
```

Create `mock_mulesoft.py`:

```python
from fastapi import FastAPI, Header, HTTPException
app = FastAPI()

@app.post("/receipts")
def receipts(payload: dict, x_correlation_id: str | None = Header(default=None)):
    if payload.get("document_id") == "force-500":
        raise HTTPException(status_code=500, detail="forced failure")
    return {
        "accepted": True,
        "document_id": payload.get("document_id"),
        "correlation_id": x_correlation_id,
    }
```

Run:

```powershell
uvicorn mock_mulesoft:app --host 127.0.0.1 --port 8080
```

Sender:

```python
import requests
r = requests.post(
    "http://127.0.0.1:8080/receipts",
    json=payload,
    headers={"X-Correlation-Id": payload["correlation_id"]},
    timeout=10,
)
r.raise_for_status()
```

## Contract questions

- synchronous API, queue, or poll?
- authentication?
- mandatory headers?
- maximum payload?
- acknowledgement schema?
- timeout?
- retryable status codes?
- duplicate/idempotency key?
- ordering?
- schema version negotiation?

## Failure matrix

| Response | POC behavior |
|---|---|
| 2xx | mark accepted |
| 4xx schema/auth | usually do not blind-retry; route for investigation |
| 429 | retry/backoff according to agreed policy |
| 5xx | retry then DLQ according to agreed policy |
| timeout | retry only if handoff is idempotent |

The real policy must be agreed with MuleSoft.

## Success criteria

- correlation ID is preserved,
- payload schema is validated,
- 2xx/4xx/5xx/timeout paths are tested,
- retries cannot create uncontrolled duplicate business actions.

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
