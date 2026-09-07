# POC 01 — S3 Receipt Ingestion and IAM

## Objective

Create a safe input bucket/prefix, upload synthetic receipt images, inspect object metadata, and access them from Python with least-privilege-style permissions.

## Why it matters

The kickoff starts after receipt images are stored in S3. Every later OCR POC depends on correctly identifying bucket, key, object version/ETag, Region, and permissions.

## Flow

`local synthetic receipt -> S3 incoming/ -> Python head_object/list/get metadata`

## Console steps

1. Open S3.
2. Create a bucket in the approved Region.
3. Keep **Block all public access** enabled.
4. Enable versioning for the POC if permitted.
5. Create prefixes:
   - `incoming/`
   - `raw-textract/`
   - `normalized/`
   - `failed/`
6. Upload `sample_receipt_001.png` under `incoming/`.

## CLI steps

```powershell
$env:BUCKET="replace-me-brinks-ocr-poc"
aws s3 cp .\samples\sample_receipt_001.png "s3://$env:BUCKET/incoming/sample_receipt_001.png"
aws s3api head-object --bucket $env:BUCKET --key incoming/sample_receipt_001.png
```

## Python test

Create `scripts/check_s3.py`:

```python
import os, boto3
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
bucket = os.environ["BUCKET"]
key = "incoming/sample_receipt_001.png"
r = s3.head_object(Bucket=bucket, Key=key)
print({
    "ContentLength": r["ContentLength"],
    "ContentType": r.get("ContentType"),
    "ETag": r.get("ETag"),
    "VersionId": r.get("VersionId"),
})
```

Run:

```powershell
$env:BUCKET="replace-me-brinks-ocr-poc"
python .\scripts\check_s3.py
```

## Negative tests

- Use a wrong key -> expect 404/NoSuchKey behavior.
- Remove `s3:GetObject` from the test role -> expect AccessDenied.
- Upload unsupported/non-image content with `.png` extension -> later OCR POC should reject/flag it.

## Success criteria

- You can upload and locate a synthetic receipt.
- Python can read its metadata.
- Bucket is not public.
- You can explain which IAM actions are required and why.
- You record bucket/key/ETag as potential idempotency inputs.

## Production hardening

- KMS requirements must come from Brinks security design.
- Apply prefix-scoped permissions.
- Consider bucket policy restrictions.
- Decide versioning/retention with the project team.
- Never log receipt contents.

## Questions for Brinks

- Input bucket already exists?
- Which prefix/event identifies a ready-to-process receipt?
- Is object versioning enabled?
- What encryption key is required?
- Does bank/layout identity arrive in metadata or filename?

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
