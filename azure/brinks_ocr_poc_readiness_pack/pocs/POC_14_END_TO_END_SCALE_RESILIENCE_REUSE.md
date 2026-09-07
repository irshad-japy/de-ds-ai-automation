# POC 14 — End-to-End Scale, Resilience, and Reusable Framework

## Objective

Prove the complete pipeline under concurrency and common failure conditions, then package the solution so a new receipt format can be added with minimal code change.

## End-to-end test

```text
synthetic receipts
-> S3 incoming
-> intake queue
-> OCR
-> raw result
-> normalization
-> validation
-> normalized payload
-> mock MuleSoft
-> final state
```

## Test batches

Start small:
- 10 documents
- 50 documents
- 100 documents

Do not run large cost-generating loads without approval.

## Failure injection

- duplicate S3 event
- malformed file
- unsupported format
- low-confidence critical field
- Textract throttling simulation
- Lambda exception
- SQS poison message
- state-store conditional conflict
- mock MuleSoft timeout
- mock MuleSoft 429
- mock MuleSoft 500
- duplicate handoff
- delayed completion message

## Measurements

Per format:
- document pass rate
- mandatory-field exact/normalized accuracy
- review rate
- technical failure rate

Platform:
- throughput
- p50/p95/p99 processing latency
- queue age
- retries/document
- DLQ count
- cost estimate per document/batch (using current approved pricing inputs)

## Reusable architecture

Make layout-specific behavior configuration-driven where possible:

```yaml
format_id: BANK_FORMAT_A
required_fields:
  - total
  - date
  - reference_number
queries:
  reference_number: "What is the transaction reference number?"
normalizers:
  reference_number: alphanumeric_upper
```

Do not hard-code 50 `if bank == ...` branches across Lambda functions.

## Onboarding a new format

1. add representative samples
2. add ground truth
3. run baseline
4. review failures
5. add configuration/query/adapter only if needed
6. rerun regression suite
7. approve expected accuracy
8. deploy config/schema version
9. monitor first production cohort

## Exit criteria

The final POC package should demonstrate:
- reliable event processing,
- measurable extraction quality,
- controlled exceptions,
- duplicate safety,
- replay,
- observable operations,
- schema versioning,
- a documented path to add a new receipt layout.

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
