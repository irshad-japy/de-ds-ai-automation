# POC-08 — Integrated Azure Data + AI Capstone (Poetry Edition)

This repository implements the capstone described in `POC_08_CAPSTONE_DATA_AI_PLATFORM.md`: batch + streaming ingestion, ADLS, Databricks Medallion processing, analytical serving, Document Intelligence, Azure AI Search, Microsoft Foundry RAG/agent integration, optional POC-07 ML scoring, security, monitoring, IaC, CI/CD, failure drills and cost cleanup.

The project is deliberately **beginner-first**. Prove the flow locally, then connect Azure services one at a time.

---

## 1. What you will prove

By the end of the POC you should be able to demonstrate:

1. One orders CSV flows to curated Gold.
2. Shipment events are sent through Event Hubs and can land in an ADLS Bronze destination.
3. A serving layer is refreshed (Azure SQL, Synapse, or Fabric — one is enough for the minimal demo).
4. A synthetic invoice is extracted with Document Intelligence.
5. Curated metrics + policy text are indexed in Azure AI Search using embeddings.
6. RAG answers cite the correct source.
7. The constrained assistant answers one policy question, one analytical metric question, and one mixed question.
8. Security/RBAC, governance, monitoring, CI/CD and cleanup are documented.
9. One controlled failure is demonstrated and recovered.

---

## 2. Project structure

```text
azure-data-ai-capstone-poetry/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── LICENSE
├── architecture/
│   └── architecture.md
├── common/
│   ├── auth.py
│   ├── config.py
│   ├── adls.py
│   ├── embeddings.py
│   └── search_auth.py
├── data/
│   ├── README.md
│   └── synthetic/
│       ├── orders_001.csv
│       ├── shipment_events.jsonl
│       ├── policies.json
│       └── invoice_001.pdf
├── ingestion/
│   ├── adf/
│   │   ├── README.md
│   │   └── pipeline_parameters.json
│   ├── batch/
│   │   └── upload_orders.py
│   ├── events/
│   │   ├── schema.py
│   │   ├── send_events.py
│   │   ├── receive_events_to_adls.py
│   │   └── send_malformed_event.py
│   └── functions/
│       ├── README.md
│       └── function_app.py
├── lakehouse/
│   ├── local_medallion.py
│   ├── bronze/01_bronze_orders.py
│   ├── silver/02_silver_orders.py
│   └── gold/03_gold_orders.py
├── serving/
│   ├── sql/
│   │   ├── schema.sql
│   │   └── load_gold.py
│   ├── synapse/README.md
│   └── fabric/README.md
├── ai/
│   ├── document_intelligence/extract_invoice.py
│   ├── rag/
│   │   ├── prepare_documents.py
│   │   ├── create_index.py
│   │   ├── index_documents.py
│   │   ├── query_search.py
│   │   └── rag_answer.py
│   ├── agent/
│   │   ├── README.md
│   │   ├── tools.py
│   │   ├── assistant.py
│   │   └── foundry_agent_runner.py
│   └── ml/delay_risk_tool.py
├── governance/data_governance.md
├── security/
│   ├── threat_model.md
│   └── rbac_matrix.md
├── monitoring/
│   ├── checklist.md
│   ├── health_check.py
│   └── queries/poc08_health.kql
├── infra/
│   ├── terraform/
│   └── bicep/
├── cicd/azure-pipelines.yml
├── scripts/
│   ├── bootstrap.ps1
│   ├── generate_synthetic_data.py
│   ├── verify_config.py
│   └── smoke_test.py
├── docs/
│   ├── POETRY_WINDOWS_GUIDE.md
│   ├── AZURE_PORTAL_SETUP.md
│   ├── FAILURE_DRILLS.md
│   ├── COST_CLEANUP.md
│   ├── TROUBLESHOOTING.md
│   └── DEMO_CHECKLIST.md
└── tests/
```

---

# PART A — Local setup with Poetry

## Step 0 — Prerequisites

Install:

- Python **3.12.x** (the project is intentionally pinned to 3.12).
- Poetry 2.x.
- VS Code (optional but recommended).
- Git (optional).
- Terraform 1.8+ only if you want IaC deployment.
- Azure CLI only if you want CLI/Terraform authentication. The Python POC can use browser authentication without Azure CLI.
- ODBC Driver 18 for SQL Server only if using the optional Azure SQL loader.

Verify in a new PowerShell/CMD window:

```powershell
py -3.12 --version
poetry --version
terraform version
```

If `az` is unavailable, that is not a blocker for the Python steps. See `docs/AZURE_PORTAL_SETUP.md` and set `AZURE_AUTH_MODE=browser`.

---

## Step 1 — Create the Poetry virtual environment

From the project root:

```powershell
poetry env use 3.12
poetry install
poetry env info
poetry run python --version
```

Expected:

```text
Python 3.12.x
```

### How to activate the Poetry environment

You do **not** need activation if you use `poetry run ...`.

Recommended:

```powershell
poetry run python -m scripts.smoke_test
```

If you specifically want an activated PowerShell:

```powershell
Invoke-Expression (poetry env activate)
```

If you prefer the old `poetry shell` command, install the optional Poetry shell plugin:

```powershell
poetry self add poetry-plugin-shell
poetry shell
```

See `docs/POETRY_WINDOWS_GUIDE.md`.

---

## Step 2 — Create `.env`

PowerShell:

```powershell
Copy-Item .env.example .env
```

CMD:

```cmd
copy .env.example .env
```

For local-only validation you can leave Azure values blank.

Check:

```powershell
poetry run python -m scripts.verify_config --profile local
```

Expected:

```text
[SUCCESS] Configuration check passed for selected profile(s).
```

---

## Step 3 — Run unit tests

```powershell
poetry run pytest
```

Expected: all tests pass.

Run Ruff too:

```powershell
poetry run ruff check .
```

---

## Step 4 — Regenerate synthetic data

The zip already contains sample data, but you can regenerate CSV/JSON inputs:

```powershell
poetry run python -m scripts.generate_synthetic_data
```

Verify:

```powershell
Get-ChildItem data\synthetic
```

You should see orders, events, policies and the included invoice PDF.

---

## Step 5 — Run the local Bronze -> Silver -> Gold smoke test

This is the most important first test because it proves the business data transformations before Azure complexity is added.

```powershell
poetry run python -m scripts.smoke_test
```

Expected outputs:

```text
output/bronze/orders.csv
output/silver/orders_clean.csv
output/gold/customer_metrics.csv
output/gold/gold_summary.json
[SUCCESS] Local batch -> Bronze -> Silver -> Gold smoke test passed.
```

Inspect:

```powershell
Get-Content output\gold\gold_summary.json
```

---

# PART B — Create/reuse Azure resources

Read **`docs/AZURE_PORTAL_SETUP.md`** and create/reuse only what you need.

Recommended minimal capstone resources:

- ADLS Gen2.
- Event Hubs namespace + `shipment-events`.
- Existing Databricks workspace from POC-02.
- One serving layer: Azure SQL, Synapse, or Fabric.
- Document Intelligence.
- Azure AI Search.
- Microsoft Foundry project with a chat deployment.
- Azure OpenAI-compatible embeddings deployment.
- Key Vault + Log Analytics/Application Insights if not already available.

Do not create every expensive service again if an earlier POC resource is still usable.

---

# PART C — Terraform option

The default Terraform deploys a small integration core and keeps Databricks disabled.

```powershell
cd infra\terraform
Copy-Item terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars
```

Set your subscription id. Then:

```powershell
terraform fmt -recursive
terraform init
terraform validate
terraform plan -out poc08.tfplan
terraform apply poc08.tfplan
terraform output
```

Copy Terraform outputs into root `.env`.

Return to project root:

```powershell
cd ..\..
```

If you cannot use Azure CLI for Terraform authentication yet, create resources manually in the portal first and run Terraform later as a separate IaC exercise.

---

# PART D — Configure `.env` and verify each service separately

## Step 6 — ADLS configuration

Fill:

```env
AZURE_AUTH_MODE=browser
ADLS_ACCOUNT_URL=https://<storage>.dfs.core.windows.net
ADLS_FILE_SYSTEM=datalake
```

Verify:

```powershell
poetry run python -m scripts.verify_config --profile adls
```

Then upload the batch file:

```powershell
poetry run python -m ingestion.batch.upload_orders
```

Verify in Azure portal:

`Storage account -> Data storage -> Containers -> datalake -> raw -> orders -> orders_001.csv`

**Success condition:** the file exists in ADLS.

---

## Step 7 — ADF batch path (optional but recommended for final architecture story)

If you already created ADF in POC-01, reuse it. Follow `ingestion/adf/README.md` to create `pl_ingest_orders_to_adls` or show your existing Copy pipeline.

**Success condition:** a manually triggered ADF run is green and a new file appears under `raw/orders/`.

For a five-minute demo, either ADF or the Python uploader can be the live run; explain that ADF is the orchestration pattern.

---

# PART E — Databricks Medallion

## Step 8 — Upload notebooks

In Databricks workspace:

1. Create/import notebook `01_bronze_orders.py`.
2. Create/import notebook `02_silver_orders.py`.
3. Create/import notebook `03_gold_orders.py`.
4. Attach temporary compute.
5. Give Databricks access to ADLS using the identity method you used in POC-02.
6. Set the notebook widget paths to your real ABFSS locations.

Example paths:

```text
abfss://datalake@<storage>.dfs.core.windows.net/raw/orders
abfss://datalake@<storage>.dfs.core.windows.net/bronze/orders
abfss://datalake@<storage>.dfs.core.windows.net/silver/orders
abfss://datalake@<storage>.dfs.core.windows.net/gold/customer_metrics
```

Run in order: Bronze -> Silver -> Gold.

**Verify Bronze:** row count > 0 and `source_file`/`ingestion_ts` exist.

**Verify Silver:** duplicates removed, types cast, invalid quantity/price filtered, `line_amount` created.

**Verify Gold:** one row per customer with `total_orders`, `total_units`, `total_revenue`.

Terminate compute after the test.

---

# PART F — Event Hubs

## Step 9 — Configure Event Hubs

Fill:

```env
EVENTHUB_FULLY_QUALIFIED_NAMESPACE=<namespace>.servicebus.windows.net
EVENTHUB_NAME=shipment-events
EVENTHUB_CONSUMER_GROUP=$Default
```

Verify:

```powershell
poetry run python -m scripts.verify_config --profile events
```

If using browser/Entra auth, make sure your user has Data Sender and Data Receiver roles.

## Step 10 — Send shipment events

```powershell
poetry run python -m ingestion.events.send_events
```

Expected:

```text
[SUCCESS] Sent 3 shipment events to Event Hubs
```

Check Event Hubs metrics for incoming messages.

## Step 11 — Receive events and write them to ADLS Bronze

Run receiver in one terminal:

```powershell
poetry run python -m ingestion.events.receive_events_to_adls --max-events 3
```

If it is waiting, send events again from a second terminal:

```powershell
poetry run python -m ingestion.events.send_events
```

**Success condition:** a JSONL file appears under `datalake/bronze/events/`.

For a production-like path, Event Hubs Capture, Stream Analytics, Functions or Databricks Structured Streaming can replace the simple consumer.

---

# PART G — Serving layer

Choose one minimal serving path.

## Option 1 — Azure SQL

Run `serving/sql/schema.sql` in your Azure SQL database.

Install optional dependency:

```powershell
poetry install --with sql
```

Set:

```env
AZURE_SQL_ODBC_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:<server>.database.windows.net,1433;Database=<db>;Encrypt=yes;TrustServerCertificate=no;Authentication=ActiveDirectoryInteractive;
```

Load local Gold result:

```powershell
poetry run python -m serving.sql.load_gold
```

Verify:

```sql
SELECT * FROM dbo.v_customer_metrics ORDER BY total_revenue DESC;
```

## Option 2 — Synapse

Follow `serving/synapse/README.md` and expose Gold through a serverless external table/view.

## Option 3 — Fabric

Follow `serving/fabric/README.md` and expose Gold through OneLake/Lakehouse/Warehouse.

**Success condition:** one curated analytical query returns the latest Gold data.

---

# PART H — Document Intelligence

## Step 12 — Configure

Fill:

```env
DOCUMENTINTELLIGENCE_ENDPOINT=https://<name>.cognitiveservices.azure.com/
DOCUMENTINTELLIGENCE_API_KEY=<key>
```

Verify:

```powershell
poetry run python -m scripts.verify_config --profile documents
```

Run:

```powershell
poetry run python -m ai.document_intelligence.extract_invoice --file data/synthetic/invoice_001.pdf
```

Expected:

```text
output/document_intelligence/invoice_001_result.json
[SUCCESS] Full extraction saved ...
```

Verify that invoice number/vendor/total are extracted reasonably. The exact fields can vary with model interpretation.

---

# PART I — Prepare Azure AI Search + embeddings

## Step 13 — Prepare searchable documents

First make sure local Gold exists:

```powershell
poetry run python -m scripts.smoke_test
poetry run python -m ai.rag.prepare_documents
```

Inspect:

```powershell
Get-Content output\search\documents.json
```

The file contains policy documents plus the latest Gold metrics summary.

## Step 14 — Configure Search and embeddings

Fill:

```env
AZURE_SEARCH_ENDPOINT=https://<search>.search.windows.net
AZURE_SEARCH_INDEX=capstone-knowledge
AZURE_SEARCH_ADMIN_KEY=<admin-key-or-blank-for-rbac>
AZURE_SEARCH_QUERY_KEY=<query-key-or-blank-for-rbac>
AZURE_OPENAI_ENDPOINT=https://<openai-resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<key-or-blank-for-rbac-if-supported-in-your-setup>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
SEARCH_VECTOR_DIMENSIONS=1536
```

Verify:

```powershell
poetry run python -m scripts.verify_config --profile search
poetry run python -m scripts.verify_config --profile embeddings
```

## Step 15 — Create vector index

```powershell
poetry run python -m ai.rag.create_index
```

Expected:

```text
[SUCCESS] Search index ready: capstone-knowledge
```

## Step 16 — Index curated documents

```powershell
poetry run python -m ai.rag.index_documents
```

Expected:

```text
[SUCCESS] Indexed 3 documents
```

The count can be higher if you add more sources.

## Step 17 — Test retrieval

```powershell
poetry run python -m ai.rag.query_search "When is a shipment considered delayed?"
```

Expected top source: `policy-shipping.md`.

Metric retrieval:

```powershell
poetry run python -m ai.rag.query_search "What is the current total revenue?"
```

Expected source: `output/gold/gold_summary.json`.

**Success condition:** retrieval returns the correct source, not merely a plausible text answer.

---

# PART J — Foundry grounded RAG

## Step 18 — Configure Foundry project

Fill:

```env
FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
FOUNDRY_MODEL_DEPLOYMENT=<your-chat-deployment>
```

Verify:

```powershell
poetry run python -m scripts.verify_config --profile foundry
```

## Step 19 — Run grounded RAG answer

```powershell
poetry run python -m ai.rag.rag_answer "When should support proactively notify a customer about a shipment delay?"
```

**Success condition:** answer is grounded in retrieved context and contains a source citation such as `[policy-shipping.md]`.

Unsupported question test:

```powershell
poetry run python -m ai.rag.rag_answer "What is the employee vacation policy?"
```

Expected: unsupported/insufficient context rather than an invented policy.

---

# PART K — Data + AI Assistant / agent tests

The safest capstone agent is application-owned and read-only. It receives only two tools: knowledge retrieval and Gold metric lookup. No write/delete tool is exposed.

## Step 20 — Policy question

```powershell
poetry run python -m ai.agent.assistant --mode policy "What is the return window for opened electronics?"
```

## Step 21 — Analytical metric question

```powershell
poetry run python -m ai.agent.assistant --mode metric "What is total revenue?"
```

## Step 22 — Mixed question

```powershell
poetry run python -m ai.agent.assistant --mode mixed "What is total revenue and when should support notify a customer about a shipment delay?"
```

**Success condition:** the answer uses the correct source/tool output and never performs a data-changing action.

### Optional Foundry Agent Service runner

If you create an agent in Foundry and set `FOUNDRY_AGENT_NAME`, run:

```powershell
poetry run python -m ai.agent.foundry_agent_runner "What is the return policy?"
```

---

# PART L — Optional POC-07 MLflow scoring

The capstone file marks prediction exposure as optional.

Offline wiring test:

```powershell
poetry run python -m ai.ml.delay_risk_tool
```

To use a real MLflow model:

```powershell
poetry install --with ml
```

Set:

```env
MLFLOW_MODEL_URI=<your-poc07-model-uri>
```

Then call `score_delay_risk(...)` from a read-only agent tool or notebook. Do not expose training/update operations to the assistant.

---

# PART M — Governance and security

Review:

```text
governance/data_governance.md
security/rbac_matrix.md
security/threat_model.md
```

For the final demo, be able to state:

- data owner;
- data classification;
- lineage;
- access roles;
- why the AI agent is read-only;
- where secrets belong in a production setup.

---

# PART N — Monitoring

Local status:

```powershell
poetry run python -m monitoring.health_check
```

Azure checks:

- Event Hubs incoming messages / errors.
- ADF/Databricks latest run.
- Document Intelligence successful request.
- Azure AI Search query latency.
- Foundry trace/model latency.
- Application Insights request/exception counts if wired.
- Cost Management.

Starter KQL: `monitoring/queries/poc08_health.kql`.

Use `monitoring/checklist.md` to capture your screenshots.

---

# PART O — Failure drill

Safest drill:

```powershell
poetry run python -m ingestion.events.send_malformed_event
```

Expected:

```text
[EXPECTED FAILURE] ... missing required fields ...
[RECOVERY] ...
```

Then prove the valid event path still works:

```powershell
poetry run python -m ingestion.events.send_events
```

Other drills are documented in `docs/FAILURE_DRILLS.md`.

---

# PART P — CI/CD

The sanitized Azure DevOps pipeline is in:

```text
cicd/azure-pipelines.yml
```

It validates:

- Poetry/Python project;
- Ruff;
- unit tests;
- Terraform formatting/validation;
- Bicep build.

Deployment is blocked unless `ENABLE_DEPLOY=true`, and the YAML contains no credential values.

Before using it, create an Azure DevOps service connection and replace the placeholder name `POC08-SERVICE-CONNECTION` with your connection name.

---

# PART Q — Final verification checklist

Run these in order from a clean clone/unzip:

```powershell
# 1. Environment
poetry env use 3.12
poetry install
poetry run python --version

# 2. Code quality and local pipeline
poetry run ruff check .
poetry run pytest
poetry run python -m scripts.smoke_test

# 3. ADLS
poetry run python -m scripts.verify_config --profile adls
poetry run python -m ingestion.batch.upload_orders

# 4. Event Hubs
poetry run python -m scripts.verify_config --profile events
poetry run python -m ingestion.events.send_events
# receiver in separate terminal if desired

# 5. Document Intelligence
poetry run python -m scripts.verify_config --profile documents
poetry run python -m ai.document_intelligence.extract_invoice

# 6. Search
poetry run python -m ai.rag.prepare_documents
poetry run python -m ai.rag.create_index
poetry run python -m ai.rag.index_documents
poetry run python -m ai.rag.query_search "When is a shipment considered delayed?"

# 7. RAG
poetry run python -m ai.rag.rag_answer "When is a shipment considered delayed?"

# 8. Agent
poetry run python -m ai.agent.assistant --mode policy "What is the return window?"
poetry run python -m ai.agent.assistant --mode metric "What is total revenue?"
poetry run python -m ai.agent.assistant --mode mixed "What is total revenue and what is the delay policy?"

# 9. Failure drill
poetry run python -m ingestion.events.send_malformed_event

# 10. Monitoring local snapshot
poetry run python -m monitoring.health_check
```

Also verify in Azure UI:

- [ ] Raw orders file exists in ADLS.
- [ ] Databricks Bronze/Silver/Gold completed.
- [ ] Event Hubs received messages.
- [ ] Selected serving view returns Gold data.
- [ ] Document Intelligence extraction succeeded.
- [ ] Search index contains current docs/metrics.
- [ ] RAG cites the correct source.
- [ ] Policy / metric / mixed agent tests pass.
- [ ] RBAC/governance documentation completed.
- [ ] Monitoring evidence captured.
- [ ] Failure drill captured.
- [ ] Cleanup completed.

---

# PART R — Cost cleanup

Read `docs/COST_CLEANUP.md`.

If Terraform created the dedicated lab resources:

```powershell
cd infra\terraform
terraform destroy
```

Then verify the resource group and Cost Management before finishing the POC.

---

# Final five-minute demo

Use `docs/DEMO_CHECKLIST.md`:

1. architecture;
2. raw input;
3. pipeline run;
4. Gold table;
5. search retrieval;
6. assistant answer + citation/tool source;
7. monitoring;
8. security;
9. cleanup.

Do not use the CV bullets until you have actually completed and verified the corresponding pieces.
