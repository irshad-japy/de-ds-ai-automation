# Brinks Receipt OCR — POC Readiness Pack

This pack converts the initial kickoff notes into a practical preparation path for the Brinks receipt OCR automation.

## Important status

The kickoff notes say the detailed solution design was still in progress. Therefore this pack is a **POC/readiness package**, not the final Brinks architecture.

### Source-established flow

`S3 receipt images -> OCR with Amazon Textract -> queue/table/JSON (TBD) -> MuleSoft -> iCash`

### Main technical risk

Supporting 50+ receipt layouts while extracting the correct business fields reliably.

## Read in this order

1. `IMPROVED_PROMPT.md`
2. `00_KICKOFF_ANALYSIS.md`
3. `01_NINE_WEEK_POC_ROADMAP.md`
4. `02_ARCHITECTURE_DECISION_QUESTIONS.md`
5. POCs in numeric order.

## POCs

- POC 01 — S3 Receipt Ingestion and IAM
- POC 02 — Textract DetectDocumentText Baseline
- POC 03 — Textract AnalyzeExpense
- POC 04 — Multi-Format Accuracy Benchmark
- POC 05 — Canonical JSON Normalization
- POC 06 — Queries / Custom Queries
- POC 07 — Confidence and Exception Flow
- POC 08 — S3 -> SQS -> Lambda
- POC 09 — Async Textract + SNS/SQS
- POC 10 — Idempotency + Processing State
- POC 11 — Queue/Table/S3 JSON Bakeoff
- POC 12 — MuleSoft Mock Handoff
- POC 13 — Observability/Security/Retry/DLQ
- POC 14 — End-to-End Scale/Resilience/Reuse

## Recommended scratch repo

```text
brinks-receipt-ocr-poc/
├─ README.md
├─ docs/
├─ samples/
│  ├─ FORMAT_A/
│  ├─ FORMAT_B/
│  └─ FORMAT_C/
├─ ground_truth/
│  └─ ground_truth.csv
├─ src/
│  ├─ handlers/
│  ├─ extractors/
│  ├─ mappers/
│  ├─ validators/
│  ├─ integrations/
│  ├─ state/
│  └─ observability/
├─ scripts/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ benchmark/
├─ infra/
└─ output/
   ├─ raw_textract/
   ├─ normalized/
   └─ reports/
```

## First seven POCs to do if time is limited

1. POC 02 — raw OCR
2. POC 03 — AnalyzeExpense
3. POC 04 — benchmark
4. POC 05 — canonical schema
5. POC 07 — confidence/exception path
6. POC 08 — event pipeline
7. POC 10 — idempotency

## AWS technical notes used while preparing this pack

- Textract supports receipt/invoice analysis through AnalyzeExpense and asynchronous StartExpenseAnalysis/GetExpenseAnalysis.
- Textract returns confidence scores; threshold policy should match the use case.
- S3 event notifications are at-least-once and may be duplicated/out of order.
- Lambda + SQS consumers should be idempotent; partial batch responses and DLQs are useful for controlled retries.
- DynamoDB conditional writes can be used to prevent overwriting an already-claimed processing key.
- CloudWatch structured logs/metrics should avoid sensitive payloads and high-cardinality metric dimensions.

Always verify these patterns against the Brinks-approved architecture, account controls, and current AWS service documentation before production implementation.
