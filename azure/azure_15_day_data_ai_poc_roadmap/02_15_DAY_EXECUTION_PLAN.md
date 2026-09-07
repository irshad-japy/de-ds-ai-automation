# 15-Day Execution Plan

## Time split

- **Days 1–7:** Data Engineering
- **Days 8–14:** AI Engineering
- **Day 15 morning:** Data Engineering integration
- **Day 15 afternoon:** AI Engineering integration

This produces an exact practical split of approximately **7.5 days Data Engineering / 7.5 days AI Engineering**.

| Day | Track | Main work | End-of-day evidence | Git goal |
|---|---|---|---|---|
| 1 | DE | Azure foundation, resource groups, budget, ADLS Gen2, Key Vault, Entra/RBAC, naming/tags | Storage + Key Vault + budget configured | `day01-foundation` |
| 2 | DE | POC-01 ADF batch ingestion, Azure SQL target, Managed Identity, monitoring; optional SHIR local source | Successful parameterized ADF load + rerun | `poc01-complete` |
| 3 | DE | POC-02 Databricks workspace, Unity Catalog concepts, Bronze ingestion, PySpark | Bronze Delta tables | `poc02-bronze` |
| 4 | DE | Silver quality/dedup/schema evolution, Auto Loader pattern, quarantine | Silver tables + bad-record path | `poc02-silver` |
| 5 | DE | Gold star schema, Delta MERGE/CDF/CDC/SCD, Spark tuning and job monitoring | Incremental load demonstrated | `poc02-complete` |
| 6 | DE | POC-03 Event Hubs streaming + Databricks/Fabric Real-Time path | Real-time events captured | `poc03-streaming` |
| 7 | DE | Fabric/OneLake/Synapse serving, Semantic Model, Purview/lineage, Monitor/Log Analytics | Curated query + lineage/monitoring | `poc03-complete` |
| 8 | AI | POC-04 Document Intelligence: synthetic invoices → extraction → ADLS | Extracted structured JSON | `poc04-extract` |
| 9 | AI | Normalize extracted data with Functions/Databricks/ADF, validation + monitoring | Invoice table + exception flow | `poc04-complete` |
| 10 | AI | POC-05 Microsoft Foundry project/model + Azure AI Search index + embeddings | Search index returns relevant chunks | `poc05-index` |
| 11 | AI | Hybrid/vector RAG + citations + evaluation + secure config | RAG answers with grounding | `poc05-complete` |
| 12 | AI | POC-06 Foundry agent, read-only tools over curated data | Agent answers structured questions | `poc06-agent` |
| 13 | AI | Tracing/evaluation/guardrails/App Insights; failure cases | Trace + evaluation report | `poc06-complete` |
| 14 | AI | POC-07 Azure ML + MLflow experiment/model registry/endpoint or batch scoring | Registered model + reproducible run | `poc07-complete` |
| 15 AM | DE | POC-08 connect ingestion → lakehouse → curated serving; CI/CD + IaC validation | Fresh redeploy/run from README | `capstone-data` |
| 15 PM | AI | Connect curated Gold → Search/Foundry → agent/RAG; final tests, cost cleanup, CV notes | Demo script + final architecture | `capstone-complete` |

## Daily operating rhythm

1. **20 min:** read the POC section for the day.
2. **90–150 min:** deploy/build the smallest working path.
3. **45–90 min:** add reliability/security/monitoring.
4. **30 min:** deliberately break one component and recover it.
5. **20 min:** capture evidence and update README.
6. **10 min:** check cost.
7. **10 min:** commit only sanitized files.

## Definition of done

A day is complete only when:

- the expected output exists;
- you can rerun the key step;
- logs are visible;
- secrets are not in Git;
- cost has been checked;
- cleanup is documented;
- you can answer “why this service?” in two sentences.
