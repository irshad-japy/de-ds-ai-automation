# POC 05 — Canonical Receipt JSON Normalization

## Objective

Create a stable schema that hides layout/provider differences from MuleSoft/iCash.

## Why it matters

Fifty bank layouts should not produce fifty downstream contracts.

## Principle

`Textract-specific response -> mapper -> canonical_receipt_v1 -> validator -> handoff`

Use `templates/canonical_receipt_schema.json` as a discussion/POC schema only.

## Suggested code structure

```text
src/
  models/
    canonical.py
  extractors/
    textract_expense.py
  mappers/
    base.py
    generic_expense.py
    bank_format_overrides.py
  validators/
    receipt_validator.py
```

## Mapper sketch

```python
TYPE_MAP = {
    "TOTAL": "total",
    "INVOICE_RECEIPT_DATE": "date",
    "INVOICE_RECEIPT_ID": "reference_number",
    "VENDOR_NAME": "issuer_name",
}

def map_summary_fields(summary_fields):
    fields = {}
    for item in summary_fields:
        provider_type = item.get("type")
        canonical = TYPE_MAP.get(provider_type)
        if canonical:
            fields[canonical] = {
                "value": item.get("value"),
                "confidence": item.get("value_confidence"),
                "source_label": item.get("label"),
            }
    return fields
```

## Versioning

Add:
```json
"schema_version": "1.0"
```

Never silently change meanings under the same schema version.

## Validation

Keep extraction and validation separate:
- extraction says what Textract observed,
- mapping says where it belongs,
- validation says whether it is acceptable.

## Tests

- same semantic receipt field under different source labels
- missing optional field
- missing mandatory field
- amount normalization
- date normalization
- duplicate field candidates
- unknown provider type
- bank/layout-specific override

## Success criteria

- three different layout formats produce the same canonical key set.
- raw provider output is still traceable.
- each normalized field preserves confidence where available.
- schema validation catches malformed payloads.

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
