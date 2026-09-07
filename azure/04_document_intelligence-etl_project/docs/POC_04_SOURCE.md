# POC-04 — Intelligent Document ETL with Azure AI Document Intelligence

## Objective

Convert unstructured synthetic invoices into validated analytical data.

## Business flow

```text
Synthetic invoice PDF/image
   |
   v
ADLS Gen2 /incoming
   |
   v
Azure AI Document Intelligence
   |
   v
Extracted JSON
   |
   +--> validation
   |      +--> quarantine
   v
Azure Functions / ADF / Databricks normalization
   |
   v
Azure SQL / Delta curated invoice table
```

## Services

- Azure AI Document Intelligence
- ADLS Gen2
- Azure Functions
- ADF or Databricks
- Azure SQL/Delta
- Key Vault
- Managed Identity/RBAC
- Application Insights / Monitor

## Cost guardrails

- Use only a few synthetic invoices.
- Choose a free tier if it is offered for the service/region.
- Do not upload real financial documents.
- Delete the cognitive/Foundry tool resource after validation if not needed.

## Steps

### 1. Create 5–10 synthetic invoices

Use fictional names, addresses and account numbers.

Fields:

```text
invoice_number
invoice_date
supplier_name
customer_name
currency
line_items[]
subtotal
tax
total
```

### 2. Store them under ADLS

```text
documents/incoming/
documents/processed/
documents/failed/
```

### 3. Create Document Intelligence resource/tool

Use the current portal experience available in your subscription.

### 4. Start with a prebuilt invoice model

Process one invoice manually in the studio/portal first.

Record:

- detected fields
- confidence scores
- missed fields

### 5. Automate extraction

Write a small Python or Function app that:

1. receives blob name;
2. submits document;
3. polls/awaits result;
4. maps fields to a stable internal schema;
5. writes normalized JSON.

Credentials must come from Managed Identity/Key Vault/environment, never source code.

### 6. Validate business rules

Examples:

- invoice number required
- total > 0
- sum(line_items) approximately equals subtotal
- subtotal + tax approximately equals total
- confidence threshold for critical fields

### 7. Route exceptions

Low confidence or invalid totals:

```text
documents/failed/
```

Save a failure reason.

### 8. Curate data

Flatten headers and lines into:

```text
invoice_header
invoice_line
```

Load to Azure SQL or Delta.

### 9. Add observability

Measure:

- documents processed
- success/failure
- average processing latency
- low-confidence field count

Use Application Insights for Function telemetry where practical.

## Validation

- At least five invoices processed.
- One malformed invoice goes to failed/quarantine.
- Reprocessing the same blob does not duplicate output.
- Header total reconciles with line totals.
- No real documents are used.

## GitHub artifacts

```text
src/
  extract_invoice.py
  validate_invoice.py
schemas/
  invoice_schema.json
docs/
  confidence_rules.md
  sample_redacted_output.json
```

Commit only synthetic/redacted examples.

## Interview questions

1. OCR vs Document Intelligence?
2. Why persist raw + extracted JSON?
3. How do confidence thresholds affect automation?
4. How would human-in-the-loop review work?
5. How do you prevent duplicate processing?
6. How would you scale to millions of documents?

## CV text — USE ONLY AFTER COMPLETION

- Built an Azure AI Document Intelligence ingestion pipeline to extract structured data from synthetic invoices into validated SQL/Delta tables.
- Added confidence-based quality rules, reconciliation, quarantine handling and idempotent document processing.
- Integrated Azure Functions, ADLS Gen2 and identity-based security with telemetry for processing success, latency and exceptions.
