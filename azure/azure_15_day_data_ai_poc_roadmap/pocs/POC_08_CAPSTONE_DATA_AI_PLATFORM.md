# POC-08 — Integrated Azure Data + AI Capstone

## Objective

Connect the best components from the first seven POCs into one interview-ready architecture.

## End-to-end architecture

```text
Synthetic batch files --------\
                               \
Synthetic real-time events -----> Ingestion
                                 |  ADF / Event Hubs / Functions
Synthetic documents -----------/
                                 |
                                 v
                           ADLS Gen2
                                 |
                                 v
                    Databricks Medallion
                   Bronze -> Silver -> Gold
                                 |
                +----------------+----------------+
                |                                 |
                v                                 v
        Fabric / OneLake                  Synapse / Azure SQL
        Warehouse / RTI                   analytical serving
                |                                 |
                +---------------+-----------------+
                                |
                                v
                       Azure AI Search
                     vector + hybrid index
                                |
                                v
                       Microsoft Foundry
                       RAG / Agent Service
                                |
                                v
                       Data + AI Assistant

Cross-cutting:
Entra ID | RBAC | Managed Identity | Key Vault
Purview / Unity Catalog
Azure Monitor | Log Analytics | Application Insights
Terraform/Bicep | Azure DevOps YAML | Cost Management
```

## Day-15 morning — Data Engineering integration

### 1. Fresh deployment test

From a clean clone, deploy only the minimal set required for the demo.

### 2. Run batch ingestion

One new orders file must flow to curated Gold.

### 3. Run event flow

Send a few shipment events and confirm they appear in the selected real-time/Delta destination.

### 4. Refresh serving layer

Update Synapse/Fabric/Azure SQL curated view.

### 5. Validate governance

Document:

- data owner
- data classification
- lineage
- access roles

### 6. CI/CD

Create an Azure DevOps YAML pipeline or an equivalent sanitized pipeline file that can:

- validate Python;
- validate Terraform/Bicep;
- run unit tests;
- deploy only when explicitly enabled.

Keep credentials in Azure DevOps service connections/variable groups or federated identity, not YAML.

## Day-15 afternoon — AI integration

### 7. Refresh AI Search

Index newly curated documents/metadata.

### 8. Run RAG tests

Ensure answers cite the right source.

### 9. Run agent tests

The agent should answer:

- one policy question;
- one analytical metric question;
- one mixed question.

### 10. Add prediction result

Optionally expose POC-07 delay-risk scoring as a safe read-only tool.

### 11. Observability dashboard/checklist

Capture:

```text
latest batch status
stream freshness
document extraction success
search latency
agent/model latency
tool failure count
cost check
```

### 12. Failure drill

Pick one:

- revoke storage permission;
- send malformed event;
- upload malformed document;
- query an unsupported RAG question.

Show controlled failure + recovery.

### 13. Cost cleanup

Delete or stop:

- Databricks compute
- Azure ML endpoint/compute
- temporary Foundry deployments if not needed
- Event Hubs if lab complete
- paid Search tier if used
- temporary resource groups

## GitHub repository structure

```text
azure-data-ai-capstone/
  README.md
  architecture/
    architecture.md
  data/
    README.md
    synthetic/
  ingestion/
    adf/
    events/
    functions/
  lakehouse/
    bronze/
    silver/
    gold/
  serving/
    synapse/
    fabric/
    sql/
  ai/
    document_intelligence/
    rag/
    agent/
    ml/
  infra/
    terraform/
    bicep/
  cicd/
    azure-pipelines.yml
  monitoring/
    queries/
  security/
    threat_model.md
    rbac_matrix.md
  tests/
  .env.example
  .gitignore
  LICENSE
```

## Final demo script

In five minutes show:

1. architecture;
2. raw input;
3. pipeline run;
4. Gold table;
5. search retrieval;
6. agent answer + citation/tool trace;
7. monitoring;
8. security;
9. cost cleanup.

## Final interview story

Use this structure:

**“I built a small Azure Data + AI platform using synthetic retail data. ADF and Event Hubs handled batch/streaming ingestion into ADLS. Databricks created governed Bronze/Silver/Gold Delta data. Fabric/Synapse provided analytical serving. Document Intelligence handled unstructured invoices. Azure AI Search and Microsoft Foundry provided grounded RAG and a constrained read-only agent. I applied identity-based access, Key Vault, monitoring, IaC/CI-CD and cost controls across the stack.”**

## CV description — USE ONLY AFTER COMPLETION

**Azure Data + AI Engineering Platform**

Designed and implemented a cost-conscious Azure Data + AI portfolio using synthetic data, combining batch/streaming ingestion, Medallion Lakehouse processing, analytical serving, unstructured document extraction, RAG and agentic AI with security, observability and CI/CD.

### CV bullets — USE ONLY AFTER COMPLETION

- Built Azure Data Factory and Event Hubs ingestion paths into ADLS Gen2 with incremental, retry-safe and monitored processing.
- Developed Azure Databricks PySpark/Delta Bronze-Silver-Gold pipelines with MERGE, CDC/CDF, SCD, schema evolution, deduplication and data-quality controls.
- Served curated datasets through Microsoft Fabric/OneLake and Synapse/Azure SQL patterns with real-time/KQL exploration.
- Implemented Azure AI Document Intelligence for structured extraction and validation of synthetic invoices.
- Built grounded RAG using Microsoft Foundry models and Azure AI Search vector/hybrid retrieval with citations and evaluation.
- Developed a constrained Foundry agent using read-only analytical and knowledge tools with tracing and security tests.
- Added Azure ML/MLflow experiment tracking and reproducible batch/endpoint scoring for synthetic shipment-delay prediction.
- Applied Entra ID, Managed Identity, RBAC, Key Vault, governance, monitoring, IaC, CI/CD and Azure Cost Management controls.
