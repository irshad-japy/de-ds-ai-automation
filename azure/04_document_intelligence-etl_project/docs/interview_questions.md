# Interview questions and concise answers

## 1. OCR vs Azure AI Document Intelligence?

OCR mainly converts pixels into text. Document Intelligence goes further by identifying document structure and semantic fields such as invoice number, vendor, dates, totals and line items, including confidence scores.

## 2. Why persist raw + normalized JSON?

Raw output is useful for audit/debugging and future remapping. Normalized JSON gives downstream systems a stable schema even if the AI provider's output changes.

## 3. How do confidence thresholds affect automation?

Higher thresholds reduce bad automatic decisions but increase manual review/quarantine volume. Thresholds should be field-specific and measured against labeled validation data.

## 4. How would human-in-the-loop review work?

Route low-confidence or reconciliation failures to a review queue/UI, show the original invoice plus extracted fields, let a reviewer correct them, then write the approved normalized record with an audit trail.

## 5. How do you prevent duplicate processing?

This POC hashes the source bytes with SHA-256, writes a deterministic processed marker and places a UNIQUE constraint on `source_hash` in Azure SQL.

## 6. How would you scale to millions of documents?

Use event-driven ingestion, queues/Event Grid, horizontally scaled workers/Functions, partitioned storage, bulk/streaming writes, backpressure, retries/DLQ, rate-limit-aware Document Intelligence calls, idempotency, telemetry, and lifecycle policies.
