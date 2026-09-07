# Azure Data + AI Engineering — 15-Day POC Portfolio

## Purpose

This repository plan is designed for a fresh personal Microsoft Azure account and targets an even split:

- **50% Data Engineering**
- **50% AI Engineering for a Data Engineer**

The goal is not to create many disconnected demos. The goal is to create a small portfolio of connected POCs that prove you can move from **raw data → governed lakehouse → streaming/warehouse → AI retrieval/agents → monitoring/CI-CD**.

> **CV rule:** Do not claim a POC as completed experience until you have deployed it, tested it, collected evidence, and can explain the design decisions in an interview.

## 8 POCs

| POC | Track | Project |
|---|---|---|
| 01 | Data Engineering | Secure Batch Landing Zone: ADF + ADLS Gen2 + Azure SQL |
| 02 | Data Engineering | Databricks Medallion Lakehouse + Incremental CDC |
| 03 | Data Engineering | Real-Time + Fabric/Synapse + Governance |
| 04 | AI Engineering | Intelligent Document ETL with Document Intelligence |
| 05 | AI Engineering | RAG with Microsoft Foundry + Azure AI Search |
| 06 | AI Engineering | Agentic Data Assistant with Foundry Agent Service |
| 07 | AI Engineering | Azure ML + MLflow + Evaluation/LLMOps |
| 08 | 50/50 | End-to-End Data + AI Capstone |

## Recommended execution order

Complete POCs 01–03 first. They create reusable storage, curated data and security patterns. Then build POCs 04–07 on top of the same synthetic business domain. POC 08 integrates the strongest components.

## Common synthetic business domain

Use a fictional company named **Contoso Retail Analytics** with only generated data:

- customers
- products
- orders
- order_items
- shipment_events
- support_documents
- synthetic invoices

This avoids PII/licensing problems and makes all POCs tell one coherent story.

## Public GitHub safety rules

- Never commit Azure access keys.
- Never commit storage connection strings.
- Never commit SAS URLs/tokens.
- Never commit client secrets.
- Never commit database passwords.
- Never commit `.env`.
- Never commit downloaded portal configuration containing credentials.
- Use `.env.example` with placeholders only.
- Prefer Managed Identity + RBAC.
- Store secrets in Key Vault.
- Use tiny synthetic datasets.
- Use parameterized IaC.
- Keep subscription/tenant-specific values in ignored local variable files.
- Run a secret scanner before every push.

## Cost rules

1. Create one dedicated resource group per POC.
2. Set a Cost Management budget/alert before deploying compute-heavy resources.
3. Use free/trial tiers when available.
4. Use serverless/consumption options when practical.
5. Keep Databricks clusters small and terminate them immediately after a lab.
6. Avoid Synapse dedicated SQL pools for this roadmap.
7. Prefer Synapse serverless SQL for small demonstrations.
8. Keep Event Hubs throughput minimal.
9. Keep AI Search on Free tier when supported.
10. Deploy only small Foundry model capacity and test with short prompts.
11. Delete temporary Azure ML compute/endpoints after validation.
12. Run the cleanup section at the end of every POC.

## Completion evidence

For every POC keep a local `evidence/` folder (screenshots can be committed only after checking they contain no IDs/secrets). Evidence should include:

- architecture diagram
- successful pipeline/job run
- sample output
- monitoring screenshot/query
- one failure + recovery demonstration
- cost check
- security configuration summary
- cleanup result
- short `LESSONS_LEARNED.md`

## Final portfolio standard

A completed POC should be explainable in this order:

**Problem → Architecture → Security → Data flow → Failure handling → Monitoring → Cost → Trade-offs → Result**
