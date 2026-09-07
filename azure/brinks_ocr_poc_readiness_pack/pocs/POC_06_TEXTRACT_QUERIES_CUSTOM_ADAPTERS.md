# POC 06 — Textract Queries and Custom Queries Adapter Feasibility

## Objective

Test targeted questions for fields that generic extraction repeatedly misses, and determine whether a Custom Queries adapter is justified.

## Why it matters

Do not build custom ML because there are 50+ layouts unless the benchmark proves generic extraction is insufficient. This POC turns that decision into evidence.

## Phase A — Queries

Candidate questions must reflect actual document wording, for example:

- "What is the transaction reference number?"
- "What is the deposit amount?"
- "What is the branch number?"

Use only fields confirmed by the business; examples above are placeholders.

Pseudo-call:

```python
resp = textract.analyze_document(
    Document={"S3Object": {"Bucket": bucket, "Name": key}},
    FeatureTypes=["QUERIES"],
    QueriesConfig={
        "Queries": [
            {"Text": "What is the transaction reference number?", "Alias": "reference_number"}
        ]
    }
)
```

## Phase B — Custom Queries adapter

Only proceed if:
1. the same field/layout failures are repeatable,
2. enough representative labeled samples are approved,
3. expected benefit is material.

Create separate training and test sets. Include layout and image-quality variation.

## Experiment table

| Format | Field | AnalyzeExpense | Query | Adapter | Ground truth | Winner |
|---|---|---:|---:|---:|---|---|

## Success criteria

- You can quantify whether Queries improves a failed field.
- If an adapter is tested, train/test data are separate.
- You can explain added maintenance cost.
- You can recommend "use" or "do not use" based on measured results.

## Brinks confirmation required

- Can document samples be used for adapter training?
- What data-governance approval is required?
- Are adapters allowed in the target Region/account?
- Which fields justify custom behavior?

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
