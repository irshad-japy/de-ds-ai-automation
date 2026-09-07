# Improved Master Prompt

Act as a **Principal Azure Data & AI Engineer, Solution Architect, and hands-on technical mentor**.

I have created a **fresh Microsoft Azure personal account** and I want to build a **15-day portfolio of practical Azure POCs** that I can safely publish to a **public GitHub repository** and later reference in my CV **only after I have actually completed and validated each POC**.

Use my Azure Data Engineer CV as the baseline and do the following:

## Goals

1. Cover the Azure services and engineering skills already present in my CV:
   - Microsoft Fabric, OneLake, Lakehouse, Warehouse, Notebooks, Dataflows Gen2, Pipelines, Semantic Models
   - Azure Data Factory, Self-hosted Integration Runtime, ADLS Gen2, Azure Storage
   - Azure Databricks, PySpark, Spark SQL, Delta Lake, Auto Loader, MERGE, CDF, CDC/SCD, schema evolution
   - Azure Synapse Analytics, Azure SQL Database
   - Azure Event Hubs, Azure Functions
   - Microsoft Purview
   - Microsoft Entra ID, RBAC, Managed Identity, Key Vault, Private Endpoints/Private Link, VNET concepts
   - Azure DevOps, Git, YAML CI/CD
   - Terraform, Bicep, ARM templates, PowerShell
   - Azure Monitor, Log Analytics, Application Insights
   - Azure Cost Management, performance and reliability engineering

2. Split the learning/execution effort **50% Data Engineering and 50% AI Engineering for a Data Engineer**.
   - Data Engineering: 7.5 days
   - AI Engineering: 7.5 days
   - The final integrated capstone can be counted 50/50.

3. Recommend additional **high-demand Azure POCs that are missing from the CV**, prioritizing current Azure/Microsoft platform direction:
   - Microsoft Foundry (current evolution of Azure AI Foundry)
   - Azure OpenAI / Foundry Models
   - Azure AI Search with vector + hybrid retrieval
   - RAG and agentic retrieval
   - Foundry Agent Service
   - Azure AI Document Intelligence
   - Azure Machine Learning + MLflow
   - AI evaluation, tracing, observability and LLMOps
   - Azure Databricks Unity Catalog
   - Microsoft Fabric Real-Time Intelligence / Eventstream / Eventhouse / KQL
   - Optional Phase-2: API Management, Azure Container Apps, Cosmos DB, Fabric Mirroring

4. Design POCs that are:
   - Beginner-friendly but interview/CV relevant
   - Small enough for a personal Azure account
   - Cost-conscious
   - Safe for public GitHub
   - Based on synthetic or openly licensed data only
   - Reproducible with clear cleanup steps
   - Designed with Managed Identity/RBAC/Key Vault rather than embedded secrets
   - Written so no access keys, SAS tokens, connection strings, tenant secrets, API keys, passwords or private data are committed

5. For each POC, provide a dedicated Markdown implementation guide containing:
   - Objective
   - Business scenario
   - Skills learned
   - Azure services
   - Architecture
   - Prerequisites
   - Cost/safety guardrails
   - Beginner step-by-step implementation
   - Validation/tests
   - Monitoring/observability
   - Security
   - GitHub files/artifacts to commit
   - What never to commit
   - Cleanup steps
   - Interview questions
   - CV-ready project description and bullets clearly marked **USE ONLY AFTER COMPLETION**

6. Create a master 15-day schedule with:
   - Daily outcome
   - POC mapping
   - Estimated focus
   - Required evidence/screenshots/logs
   - Git commit goal
   - End-of-day validation

7. Provide a service coverage matrix showing exactly which POC practices each CV service and which new high-demand skills are added.

8. Use current 2026 terminology. Prefer **Microsoft Foundry** for new AI implementation while retaining recognizable Azure OpenAI/Azure AI Search keywords for job-market discoverability.

9. Avoid legacy-first designs. If a service has a newer recommended Microsoft platform path, explain the relationship and use the modern path where practical.

10. End with an integrated capstone that demonstrates:
    **source → ingestion → lakehouse → transformation → curated serving → AI retrieval/agent → observability/security/CI-CD**.

Output a complete execution kit suitable for a public GitHub repository.
