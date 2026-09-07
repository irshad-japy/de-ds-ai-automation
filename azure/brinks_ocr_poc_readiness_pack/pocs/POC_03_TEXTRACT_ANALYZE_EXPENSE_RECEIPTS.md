# POC 03 — Textract AnalyzeExpense for Receipts

## Objective

Use Textract's receipt/invoice-specific extraction API and convert summary fields and line items into an inspectable Python structure.

## Why it matters

The kickoff specifically concerns bank receipts. `AnalyzeExpense` is the most direct generic Textract baseline for receipt/invoice semantics.

## Flow

`S3 receipt -> AnalyzeExpense -> SummaryFields + LineItemGroups -> extracted_fields.json`

## Script

Create `scripts/analyze_expense.py`:

```python
import os, json, boto3

client = boto3.client("textract", region_name=os.getenv("AWS_REGION"))
bucket = os.environ["BUCKET"]
key = os.environ["KEY"]

resp = client.analyze_expense(
    Document={"S3Object": {"Bucket": bucket, "Name": key}}
)

def text_and_conf(d):
    if not d:
        return None, None
    return d.get("Text"), d.get("Confidence")

out = []
for doc in resp.get("ExpenseDocuments", []):
    fields = []
    for sf in doc.get("SummaryFields", []):
        type_text, type_conf = text_and_conf(sf.get("Type"))
        label_text, label_conf = text_and_conf(sf.get("LabelDetection"))
        value_text, value_conf = text_and_conf(sf.get("ValueDetection"))
        fields.append({
            "type": type_text,
            "label": label_text,
            "value": value_text,
            "value_confidence": value_conf,
        })
    out.append({"expense_index": doc.get("ExpenseIndex"), "summary_fields": fields})

print(json.dumps(out, indent=2))
with open("analyze_expense_normalized_view.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
```

Run:

```powershell
$env:BUCKET="replace-me"
$env:KEY="incoming/sample_receipt_001.png"
python .\scripts\analyze_expense.py
```

## Build a field inventory

Create a table for each representative format:

| Expected business field | Textract Type | Label | Extracted value | Confidence | Correct? |
|---|---|---|---|---:|---|

Do **not** assume Textract's normalized type names exactly match iCash field names.

## Verification

- Check total/amount/date/reference-like fields visible in the synthetic receipt.
- Compare raw OCR result from POC 02 against AnalyzeExpense result.
- Note fields read by OCR but not semantically promoted by AnalyzeExpense.

## Success criteria

- API completes successfully.
- You can inspect SummaryFields and LineItemGroups.
- You know which fields can be mapped generically.
- You have a list of missing/ambiguous fields for POC 06.

## Production hardening

- Preserve provider output separately from canonical output.
- Version the mapping logic.
- Never make a financial decision solely on a field below the agreed project confidence threshold.
- Confirm whether synchronous limits fit the real document types/size and throughput.

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
