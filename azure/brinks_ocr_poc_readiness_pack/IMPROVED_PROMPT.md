# Improved Prompt — Brinks Receipt OCR POC Preparation

I have attached `project_notes.txt`, which contains the notes from the very first Brinks project kickoff meeting.

Please use the kickoff notes as the primary source and perform a detailed technical analysis of the project. Clearly separate:
1. facts explicitly stated in the kickoff notes,
2. assumptions/inferences,
3. open questions that must be confirmed after onboarding or after the final solution design is shared.

My goal is to prepare myself technically before offshore implementation starts.

## What I need

### 1. Project understanding
Explain the project end-to-end in beginner-friendly language, including:
- business objective,
- expected flow,
- AWS services that are directly indicated or are likely candidates,
- the role of Amazon S3,
- the OCR/extraction responsibility,
- Amazon Textract options,
- the need to support 50+ bank receipt formats,
- possible queue/table/JSON handoff patterns,
- MuleSoft integration,
- iCash integration boundary,
- error handling and reprocessing,
- monitoring,
- security,
- scalability,
- reusability for future Brinks automations.

Do not treat the queue/table design as finalized because the kickoff notes explicitly say that it is still under design.

### 2. Risks and unknowns
Create a list of:
- technical risks,
- OCR/data-quality risks,
- integration risks,
- operational risks,
- security/compliance questions,
- performance/SLA questions,
- questions I should ask Mohan, Nitin, Germy, and the onsite technical leads.

### 3. POC roadmap
Create a prioritized POC roadmap that prepares me for the actual nine-week project. Start with the highest-risk OCR work and then move toward production readiness.

The roadmap should cover at minimum:
- S3 receipt ingestion,
- Textract DetectDocumentText baseline,
- Textract AnalyzeExpense,
- a benchmark across multiple receipt layouts,
- normalized/canonical receipt JSON,
- confidence scoring and exception handling,
- Textract Queries / Custom Queries adapter feasibility,
- event-driven S3 → SQS → Lambda processing,
- asynchronous Textract with SNS/SQS where appropriate,
- idempotency and processing-state tracking,
- queue vs table vs S3 JSON handoff design comparison,
- MuleSoft handoff contract using a mock endpoint/consumer,
- retries, DLQ, observability, alarms,
- security and least privilege,
- end-to-end load/resilience testing,
- reusable framework design.

### 4. One implementation Markdown file per POC
For every POC, create a separate beginner-friendly Markdown implementation guide.

Every POC Markdown file must contain:
- objective,
- why the POC matters to the Brinks project,
- architecture/flow,
- prerequisites,
- AWS Console setup steps,
- AWS CLI commands where useful,
- local Python setup,
- project/file structure,
- complete example Python snippets where useful,
- environment variables,
- execution commands in the exact order,
- verification steps,
- expected outputs,
- negative/failure test cases,
- cleanup steps,
- success criteria,
- common errors and troubleshooting,
- production hardening notes,
- what information still needs confirmation from the Brinks design team.

### 5. Nine-week alignment
Map the POCs to the nine-week delivery described in the kickoff notes, respecting that onsite leads start design first and offshore engineers begin corresponding work after that.

### 6. Safety and realism
- Use synthetic or fully redacted receipts for POCs until authorized Brinks data and environments are provided.
- Do not invent finalized MuleSoft/iCash contracts.
- Do not invent the final queue/table architecture.
- Do not assume throughput, SLA, retention, exact fields, or security classifications unless the source states them.
- Clearly label recommendations as recommendations rather than facts.

### 7. Deliverables
Produce:
- `README.md`
- `00_KICKOFF_ANALYSIS.md`
- `01_NINE_WEEK_POC_ROADMAP.md`
- `02_ARCHITECTURE_DECISION_QUESTIONS.md`
- one Markdown file for every POC,
- `templates/canonical_receipt_schema.json`
- `templates/ground_truth_template.csv`
- a ZIP containing the complete preparation pack.

Make the material practical enough that a beginner can execute each POC from scratch and verify it works.
