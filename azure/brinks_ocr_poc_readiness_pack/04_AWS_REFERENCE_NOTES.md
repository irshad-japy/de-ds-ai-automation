# 04 — AWS Reference Notes Used for the POC Pack

Checked against current AWS documentation on 2026-09-03.

## Amazon Textract

### AnalyzeExpense
Use this as the receipt/invoice-specific baseline. It returns expense documents containing summary fields and line-item groups.

### Asynchronous expense analysis
`StartExpenseAnalysis` starts asynchronous receipt/invoice analysis for documents in S3. Completion is published to an SNS topic; retrieve successful results with `GetExpenseAnalysis`. Handle pagination.

### Confidence
Textract responses include confidence scores. AWS recommends choosing thresholds according to the sensitivity of the business use case. The Brinks threshold is **not known from kickoff** and must be confirmed.

### Queries / Custom Queries
Queries can target specific fields. Custom Queries adapters can be trained from representative labeled data when base behavior needs customization. Treat adapters as a measured optimization after benchmarking.

## Amazon S3 Event Notifications

S3 event notifications are delivered at least once and are not guaranteed to be ordered. Duplicate notifications can occur. Consumers must therefore be idempotent.

If a Lambda writes to the same bucket/prefix that triggers it, configure prefixes or separate destinations to avoid recursive invocation loops.

## Lambda + SQS

Lambda polls SQS in batches. By default, a batch failure can cause successfully processed messages from that batch to become visible again. Partial batch responses can be configured so only failed records are retried.

Use a dead-letter queue for messages that repeatedly fail, with retry/redrive settings agreed by the project.

The Lambda timeout must not be greater than the SQS queue visibility timeout.

## DynamoDB conditional writes

A conditional `PutItem` with `attribute_not_exists(key)` can prevent an existing idempotency/state item from being overwritten. This is one possible building block for duplicate-safe processing, subject to final architecture approval.

## CloudWatch

Structured logs and Embedded Metric Format can produce application metrics from Lambda logs. Avoid sensitive receipt payloads in logs and avoid high-cardinality metric dimensions such as request/document IDs.

## What these references do NOT decide

AWS capabilities do not decide:
- which queue/table pattern Brinks will approve,
- whether DynamoDB is allowed,
- whether Step Functions is approved,
- the MuleSoft contract,
- the iCash field contract,
- accuracy/confidence thresholds,
- SLA/throughput,
- security classification,
- retention,
- network boundaries.

Those remain project decisions.
