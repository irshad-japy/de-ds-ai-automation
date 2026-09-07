# 01 — Nine-Week POC and Delivery Readiness Roadmap

> This is a preparation roadmap derived from the kickoff. It must be reconciled with the finalized onsite architecture when that design is issued.

## POC catalog

| POC | Topic | Primary risk reduced |
|---|---|---|
| 01 | S3 receipt ingestion + IAM | access/input mistakes |
| 02 | Textract DetectDocumentText baseline | raw OCR uncertainty |
| 03 | Textract AnalyzeExpense | receipt-field extraction |
| 04 | 50-format accuracy benchmark harness | unknown accuracy/layout variability |
| 05 | Canonical receipt JSON normalization | downstream contract instability |
| 06 | Textract Queries + Custom Queries feasibility | hard-to-extract fields |
| 07 | Confidence validation + exception routing | silent bad data |
| 08 | S3 -> SQS -> Lambda event pipeline | event/retry/concurrency issues |
| 09 | Async Textract + SNS/SQS | multipage/high-latency scaling |
| 10 | Idempotency + processing state | duplicate/retry side effects |
| 11 | Queue vs table vs S3 JSON design bakeoff | unresolved handoff design |
| 12 | MuleSoft mock handoff | integration contract risk |
| 13 | Observability, security, retries, DLQ | production operations |
| 14 | End-to-end load/resilience/reuse | scale and future reuse |

## Week-by-week alignment

### Week 1 — onsite architecture/design; offshore preparation
- Read kickoff and incoming project documents.
- Prepare synthetic receipts.
- Set up local Python/AWS CLI training environment.
- Run POCs 01–03 in an authorized sandbox if available.
- Build question list for onsite leads.
- Do not hard-code an unapproved queue/table design.

**Exit:** you can explain every layer and demonstrate Textract on synthetic receipts.

### Week 2 — offshore starts corresponding implementation
- Reconcile the final design against POCs.
- Execute POC 04 benchmark on approved representative samples.
- Implement POC 05 canonical schema.
- Start POC 07 validation rules.

**Exit:** baseline field-level measurements exist, and downstream JSON is versioned.

### Week 3 — extraction quality hardening
- Analyze failures by receipt family.
- Execute POC 06 Queries/Custom Queries experiment only on problematic fields/layouts.
- Tune preprocessing only where measurable.
- Define confidence/mandatory-field policy.

**Exit:** extraction strategy chosen by evidence, not intuition.

### Week 4 — event-driven pipeline
- Execute POC 08.
- Add DLQ and retry behavior.
- Begin POC 10 idempotency/state tracking.

**Exit:** upload -> processing is repeatable and duplicate-safe.

### Week 5 — asynchronous/scale path
- Execute POC 09 if PDFs/multipage or async throughput requires it.
- Add pagination/result retrieval.
- Archive raw Textract result and normalized result separately.

**Exit:** large/async processing has a reliable completion pattern.

### Week 6 — handoff design
- Execute POC 11 with actual agreed constraints.
- Finalize queue/table/S3 JSON responsibilities.
- Implement POC 12 mock MuleSoft contract before real endpoint integration.

**Exit:** payload contract, acknowledgement, retry ownership, and duplicate semantics are explicit.

### Week 7 — operational hardening
- Execute POC 13.
- CloudWatch dashboards/alarms.
- Security review.
- Least-privilege policies.
- DLQ replay runbook.
- Correlation IDs and audit trail.

**Exit:** failures are visible, diagnosable, and recoverable.

### Week 8 — integrated testing
- Execute POC 14.
- Load, duplicate, poison-message, Textract throttling, MuleSoft 5xx, invalid-document tests.
- Measure p50/p95/p99 latency and field accuracy.

**Exit:** quantitative evidence that the system meets the agreed acceptance criteria.

### Week 9 — release/readiness/handover
- Fix final defects.
- Document runbooks.
- Document onboarding of a new bank/layout.
- Capture reusable framework components.
- Create support dashboard and troubleshooting guide.
- Final knowledge transfer.

**Exit:** production release package and reusable automation framework.

## Daily personal study order before Week 2

Day 1: POC 01 + POC 02  
Day 2: POC 03 + inspect Textract JSON deeply  
Day 3: POC 04 + build ground-truth thinking  
Day 4: POC 05 + POC 07  
Day 5: POC 08 + POC 10  
Day 6: POC 09 + POC 11  
Day 7: POC 12 + POC 13 + failure drills
