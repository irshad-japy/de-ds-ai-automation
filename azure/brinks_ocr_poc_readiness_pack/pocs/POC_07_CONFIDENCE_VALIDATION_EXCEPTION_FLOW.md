# POC 07 — Confidence, Validation, and Exception Routing

## Objective

Prevent low-quality OCR from silently reaching MuleSoft/iCash.

## Why it matters

Textract returns confidence scores. Financial/operational automation must define what happens when a critical field is missing or uncertain.

## Policy model

Do not hard-code 90 or any other production threshold until the business approves it.

For the POC:

```python
POC_THRESHOLD = 90.0  # demonstration only, NOT a Brinks requirement

def validate(fields, required):
    missing = []
    low = []
    for name in required:
        item = fields.get(name)
        if not item or item.get("value") in (None, ""):
            missing.append(name)
            continue
        conf = item.get("confidence")
        if conf is not None and conf < POC_THRESHOLD:
            low.append(name)
    return {
        "is_valid": not missing and not low,
        "missing_required_fields": missing,
        "low_confidence_fields": low,
    }
```

## Routes

```text
VALID -> outbound
MISSING REQUIRED -> exception
LOW CONFIDENCE -> exception/review
TECHNICAL ERROR -> retry then DLQ
UNSUPPORTED FORMAT -> exception
```

Keep business/data-quality exceptions separate from technical retries.

## Tests

1. all fields present/high confidence
2. missing mandatory total
3. confidence just below threshold
4. malformed amount
5. impossible date
6. duplicate candidate fields
7. unsupported receipt type

## Success criteria

- Bad data is not marked successful.
- The reason for exception is machine-readable.
- Technical failures and business validation failures are distinguishable.
- Reprocessing can reuse the original document and correlation ID.

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
