# Azure Portal Setup — Detailed Beginner Notes

This file expands the resource-creation steps from the README.

## Recommended order

1. Resource group
2. Microsoft Foundry project/resource
3. Chat model deployment
4. Embedding model deployment
5. Azure AI Search
6. Optional Application Insights
7. Optional Key Vault
8. Local `.env`
9. Ingestion
10. Retrieval and RAG verification

## Why the order matters

You need the Foundry model endpoint/deployment names and Azure AI Search endpoint before the Python project can be configured.

## Foundry model deployment names

The `model=` value sent by the Python OpenAI client is your deployment name. If you call your deployment `rag-chat`, use:

```dotenv
FOUNDRY_CHAT_DEPLOYMENT=rag-chat
```

Do the same for the embedding deployment.

## Azure AI Search Free tier

Free tier is ideal for this tiny POC when available. Availability is subscription/region dependent. Do not create a paid tier casually if you only want to practice; check the pricing screen before selecting Create.

## Endpoint checklist

Search endpoint:

```text
https://<search-name>.search.windows.net
```

Foundry OpenAI-compatible base URL:

```text
https://<resource-host>/openai/v1/
```

Use the exact endpoint displayed by your resource rather than fabricating it from the resource name.

## What Python creates automatically

You do NOT need to manually create the Azure AI Search index in the portal. `python -m rag.ingest` creates or updates it using the SDK, then uploads embedded chunks.
