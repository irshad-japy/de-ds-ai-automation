# POC 04 — Multi-Format OCR Accuracy Benchmark

## Objective

Create a repeatable benchmark that measures field-level extraction accuracy across representative receipt layouts.

## Why it matters

"50+ formats" is the central variability risk. A demo that works on one receipt proves almost nothing.

## Dataset structure

```text
benchmark/
  samples/
    FORMAT_A/
    FORMAT_B/
    FORMAT_C/
  ground_truth.csv
  outputs/
  reports/
```

Start with synthetic formats. Replace only with approved redacted/authorized samples later.

## Ground truth

Use `templates/ground_truth_template.csv`:

```csv
document_id,receipt_format_id,field_name,expected_value,mandatory
sample-001,FORMAT_A,total,123.45,true
```

## Metrics

Track at least:
- exact match rate by field
- normalized match rate by field
- mandatory-field completeness
- average confidence
- low-confidence rate
- document pass rate
- latency
- error rate
- results by `receipt_format_id`

## Normalization before comparison

Examples:
- strip whitespace
- uppercase identifiers
- normalize dates to agreed ISO representation
- normalize amount separators/currency
- remove formatting punctuation only when business rules allow it

Do not normalize away meaningful differences.

## Python comparison sketch

```python
def normalize(name, value):
    if value is None:
        return None
    v = str(value).strip()
    if name in {"reference_number", "branch_id"}:
        return v.upper().replace(" ", "")
    if name in {"total", "amount"}:
        return v.replace(",", "")
    return v

def is_match(field, expected, actual):
    return normalize(field, expected) == normalize(field, actual)
```

## Execution

1. Choose 3–5 synthetic layout families first.
2. Put at least 5 variants in each family (clean, rotated, lower contrast, etc.).
3. Run POC 02 and POC 03 extraction.
4. Map results to the target field inventory.
5. Compare with ground truth.
6. Produce CSV report.
7. Group errors by format and field.
8. Identify the top 3 failure causes.
9. Only then try Queries/Custom Queries or preprocessing.

## Success criteria

You can answer:
- Which fields are weakest?
- Which layouts are weakest?
- Is the problem OCR recognition or semantic extraction?
- What percentage of documents can pass automatically at the proposed threshold?
- Which layouts require a targeted strategy?

## Production acceptance

The actual target percentages must come from Brinks/iCash stakeholders. Do not invent them.

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
