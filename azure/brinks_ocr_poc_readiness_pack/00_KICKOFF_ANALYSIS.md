# 00 — Brinks Kickoff Analysis

## 1. What the kickoff notes explicitly establish

The initial flow is:

`Receipt images -> Amazon S3 -> OCR/extraction -> queue/table/JSON handoff -> MuleSoft -> iCash`

The kickoff notes explicitly state:

- Receipt images will already be stored in Amazon S3.
- The project needs OCR functions for those images.
- Different banks have different receipt layouts.
- More than 50 receipt formats must be processed.
- Amazon Textract is the named OCR technology.
- A queue/table-based handoff is being considered, but the design was not finalized at kickoff.
- MuleSoft will consume the OCR result from the agreed handoff mechanism and send it onward to iCash.
- OCR is called out as the key technical area requiring expertise.
- The delivery window is nine weeks.
- The solution is expected to be reusable and expandable to other Brinks branch/customer-support automations.
- Onsite technical leads begin design first; offshore work follows.
- Access, Brinks account, VM, and software installation are part of onboarding and will be coordinated by the Brinks/HCL leads.

## 2. What is NOT finalized in the kickoff notes

Do not assume these items are decided:

- SQS vs DynamoDB vs database vs S3 JSON for the downstream handoff.
- Exact canonical fields required by iCash.
- Exact MuleSoft message/API contract.
- Whether OCR must use synchronous or asynchronous Textract APIs.
- Whether `DetectDocumentText`, `AnalyzeDocument`, `AnalyzeExpense`, Queries, or Custom Queries adapters will be the final extraction approach.
- Expected files: JPEG/PNG only vs PDF/TIFF as well.
- Throughput and peak concurrency.
- SLA/latency.
- Retention.
- encryption/KMS requirements.
- required AWS Region.
- exact IAM model.
- reprocessing rules.
- human-review workflow.
- acceptable accuracy/confidence thresholds.
- what constitutes a duplicate receipt.
- whether bank/layout classification exists upstream.

## 3. Recommended technical interpretation

The highest project risk is not simply "calling OCR." It is reliably extracting the **business fields iCash needs** from more than 50 visual layouts, normalizing them into one stable contract, and doing that in a retry-safe, observable, secure pipeline.

Therefore the POCs should deliberately separate these layers:

1. **Ingestion** — prove receipt objects and metadata can be handled safely.
2. **OCR baseline** — inspect raw detected text.
3. **Receipt-aware extraction** — test Textract AnalyzeExpense.
4. **Accuracy harness** — measure extraction against labeled ground truth.
5. **Normalization** — convert provider-specific output into one canonical JSON.
6. **Targeted extraction** — evaluate Queries/Custom Queries when generic extraction is insufficient.
7. **Confidence policy** — route low-confidence or missing-field documents to an exception path.
8. **Event processing** — S3/SQS/Lambda and asynchronous Textract patterns.
9. **Idempotency/state** — make duplicate events/retries harmless.
10. **Integration contract** — mock the MuleSoft boundary before real connectivity is available.
11. **Operations/security** — logs, metrics, alarms, DLQ, encryption, least privilege.
12. **Scale/reuse** — load tests, failure injection, configuration-driven bank/layout rules.

## 4. Suggested extraction strategy to test, not assume

### Option A — AnalyzeExpense first
Amazon Textract's receipt/invoice-specific API returns summary fields and line-item groups. It is the most direct baseline for receipts.

### Option B — DetectDocumentText
Use this to understand what text OCR can physically read from difficult images. It is useful when an extracted business field is missing and you need to separate an OCR-recognition problem from a field-mapping problem.

### Option C — AnalyzeDocument + Queries
Use Queries for precise business fields when generic receipt semantics are insufficient.

### Option D — Custom Queries adapter
Consider this only after a benchmark identifies repeatable misses. Train/test samples should represent actual layout variation. This should be a measured improvement experiment, not the first implementation choice.

## 5. Proposed canonical pipeline layers

```text
S3 incoming/
  |
  v
Event intake
  |
  v
Idempotency/state check
  |
  v
Textract extraction
  |
  v
Raw result archive
  |
  v
Normalization to canonical receipt JSON
  |
  +--> validation/confidence OK --> outbound handoff --> MuleSoft --> iCash
  |
  +--> validation/confidence FAIL --> exception/DLQ/review/reprocess
```

## 6. Minimum metadata to carry end-to-end

Recommended, subject to final design:

- `correlation_id`
- `document_id`
- `source_bucket`
- `source_key`
- `source_etag` or object version where available
- `bank_id` if known
- `receipt_format_id` if known
- `received_at`
- `ocr_engine`
- `ocr_api`
- `processing_status`
- `attempt_count`
- `normalized_payload_version`
- `validation_status`
- `error_code`
- `error_message`

Do not put credentials or sensitive receipt data into operational log lines.

## 7. Questions to ask immediately after onboarding

### Business / iCash
1. Which exact receipt fields must iCash receive?
2. Which fields are mandatory vs optional?
3. What formats are expected for amount, date/time, account identifiers, branch identifiers, currency, and reference numbers?
4. What should happen when a mandatory field is unreadable?
5. Are there reconciliation rules to detect duplicates?

### Input documents
6. Do we receive JPEG, PNG, PDF, TIFF, or a mixture?
7. Are documents single-page only?
8. What are typical/max file sizes and resolutions?
9. Are images rotated, skewed, blurred, cropped, handwritten, or low contrast?
10. Do filenames/prefixes/metadata identify bank or receipt type?

### OCR accuracy
11. What field-level accuracy is required?
12. Is there an approved confidence threshold?
13. Is manual review allowed/required?
14. Is there a representative labeled sample set for all 50+ formats?
15. Which formats are highest volume and highest business risk?

### AWS architecture
16. Which AWS account/Region/VPC are used?
17. Does Textract need to operate through specific network/security controls?
18. What encryption key/policy is required?
19. Is Step Functions part of the approved pattern?
20. Is SQS the preferred buffer?
21. Is DynamoDB or another data store approved for processing state?
22. Where should raw and normalized OCR JSON be retained?

### MuleSoft
23. Will MuleSoft poll a table/queue or receive an API/event?
24. What is the payload schema and max message size?
25. How is authentication handled?
26. What acknowledgement means "success"?
27. How are 4xx vs 5xx responses handled?
28. Who owns retries between AWS and MuleSoft?
29. Is ordering required?
30. How are duplicate messages detected?

### Operations
31. Expected average/peak receipts per minute/hour/day?
32. End-to-end latency target?
33. RTO/RPO?
34. Retention/audit requirements?
35. Who owns DLQ remediation?
36. What dashboards/alarms are mandatory?
37. What support/runbook model applies after release?

## 8. Preparation priorities

If you have limited time before access:

1. Finish POC 02 and 03 first.
2. Build the benchmark harness in POC 04.
3. Learn normalization and confidence routing.
4. Then learn SQS/Lambda event processing and idempotency.
5. Finally practice MuleSoft mock integration and operational hardening.

This ordering matches the kickoff's statement that OCR expertise is the key part.
