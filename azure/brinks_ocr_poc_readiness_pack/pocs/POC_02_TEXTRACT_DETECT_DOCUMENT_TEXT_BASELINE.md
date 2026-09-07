# POC 02 — Textract DetectDocumentText Baseline

## Objective

Run raw OCR on a receipt and inspect `LINE` and `WORD` blocks, text, confidence, and geometry.

## Why it matters

When a business field is missing, you need to know whether Textract failed to **read the text** or your field-mapping logic failed to **interpret the text**.

## Flow

`S3 receipt -> DetectDocumentText -> raw blocks -> diagnostic text file`

## IAM

POC identity needs:
- `textract:DetectDocumentText`
- `s3:GetObject` for the input object

## Script

Create `scripts/detect_text.py`:

```python
import os, json, boto3

textract = boto3.client("textract", region_name=os.getenv("AWS_REGION"))
bucket = os.environ["BUCKET"]
key = os.environ.get("KEY", "incoming/sample_receipt_001.png")

resp = textract.detect_document_text(
    Document={"S3Object": {"Bucket": bucket, "Name": key}}
)

lines = [
    {"text": b["Text"], "confidence": b["Confidence"]}
    for b in resp["Blocks"]
    if b["BlockType"] == "LINE"
]

print("\n".join(f'{x["confidence"]:6.2f} | {x["text"]}' for x in lines))

with open("detect_document_text.json", "w", encoding="utf-8") as f:
    json.dump(resp, f, indent=2, default=str)
```

Run:

```powershell
$env:BUCKET="replace-me"
$env:KEY="incoming/sample_receipt_001.png"
python .\scripts\detect_text.py
```

## What to inspect

For every expected business value:
1. Is the text present at all?
2. What is its confidence?
3. Was a label/value split incorrectly?
4. Was punctuation/decimal placement misread?
5. Is orientation/cropping the real issue?

## Failure tests

- rotated image
- low-resolution image
- light/washed-out text
- noisy background
- cropped receipt
- handwritten annotation
- multiple receipts in one image

## Success criteria

You can identify:
- clearly read text,
- low-confidence text,
- missing text,
- geometry blocks,
- a concrete reason to use a receipt-aware API next.

## Troubleshooting

`AccessDeniedException`: verify Textract permission and S3 access.  
`InvalidS3ObjectException`: check Region, object key, permissions, and supported file.  
Poor OCR: test a cleaner source image before adding custom preprocessing.

## Production note

Raw OCR output should normally be retained separately from the normalized business payload if audit/reprocessing requirements permit it.

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
