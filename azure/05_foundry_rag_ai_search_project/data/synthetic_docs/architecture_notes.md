---
title: RAG POC Architecture Notes
source: architecture_notes.md
category: architecture
effective_date: 2026-08-01
---
# RAG POC Architecture Notes

The local Python ingestion process reads synthetic Markdown documents, chunks the text, and calls a Microsoft Foundry embedding deployment. Text, metadata, and vectors are stored in Azure AI Search. At query time, the application embeds the user query and runs vector or hybrid retrieval against Azure AI Search. Retrieved chunks are passed to a Foundry chat deployment with a grounded prompt. The FastAPI layer exposes retrieval and answer endpoints. Application Insights is optional for telemetry.
