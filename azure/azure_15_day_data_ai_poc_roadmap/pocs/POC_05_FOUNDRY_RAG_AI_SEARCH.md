# POC-05 — Enterprise RAG with Microsoft Foundry and Azure AI Search

## Objective

Build a small RAG application over your own curated/synthetic documents using current Microsoft Foundry patterns and Azure AI Search.

## Architecture

```text
Curated docs / Gold data
      |
      v
Chunk + metadata
      |
      v
Embeddings / vectorization
      |
      v
Azure AI Search
  text + vector fields
      |
      v
Hybrid retrieval
      |
      v
Microsoft Foundry model
      |
      v
Answer + citations
```

## Services

- Microsoft Foundry
- Azure OpenAI / Foundry Models
- Azure AI Search
- Azure Functions or FastAPI locally
- Key Vault / Managed Identity
- Application Insights
- Optional Foundry evaluation/tracing

## Why this POC matters

Modern Azure AI Search supports vector and hybrid retrieval. The goal is to show that you understand retrieval quality, not only how to call an LLM.

## Cost guardrails

- Use Azure AI Search Free tier if available.
- Keep the index small.
- Use 10–30 short documents.
- Limit model calls.
- Set a strict token/output limit.
- Delete paid model deployments after testing if they are not needed.
- If a specific model is unavailable due to quota/region, use another Foundry model available to your subscription and document the substitution.

## Steps

### 1. Create the knowledge corpus

Use synthetic content such as:

```text
product policies
shipping SLA
return policy
data dictionary
architecture notes
```

No copyrighted bulk content and no employer documents.

### 2. Create Microsoft Foundry project/resource

Use current Foundry terminology.

Deploy or select a small model available to your account.

### 3. Create Azure AI Search

Prefer Free tier for the POC.

Index fields:

```text
id
title
content
source
category
chunk_id
content_vector
```

### 4. Chunking

Start with simple fixed/token-aware chunking.

Document:

- chunk size
- overlap
- metadata strategy

### 5. Embeddings/vectorization

Create vector representations using a model/tool available in your Foundry setup.

Never place keys in the repo.

### 6. Index the chunks

Validate total document/chunk count.

### 7. Baseline vector search

Ask:

```text
What is the return window for damaged items?
```

Inspect top-k chunks.

### 8. Hybrid search

Combine keyword/full-text and vector retrieval.

Compare relevance with vector-only retrieval.

### 9. RAG prompt

Require:

- answer only from retrieved context;
- say “I don't have enough information” when unsupported;
- return source/citation metadata.

### 10. Evaluate retrieval

Create 10 questions with expected source documents.

Track:

```text
retrieval_hit@k
citation_correct
answer_grounded
unsupported_answer
latency
```

### 11. Failure tests

Test:

- question not in corpus
- ambiguous question
- conflicting documents
- prompt injection text inside a document

Document mitigation behavior.

### 12. Observability

Track request latency, failures and model/search calls.

Use Application Insights/Foundry tracing if supported by your chosen implementation path.

## Validation

- Correct source appears in top-k for most test questions.
- Hybrid retrieval outperforms or is at least compared against vector-only.
- Unsupported questions do not produce confident fabricated answers.
- Each answer includes source identifiers.

## GitHub artifacts

```text
rag/
  ingest.py
  retrieve.py
  app.py
eval/
  questions.json
  results_template.md
data/
  synthetic_docs/
docs/
  retrieval_experiments.md
```

## Interview questions

1. Vector search vs keyword search?
2. Why hybrid retrieval?
3. What is RRF conceptually?
4. Chunk size trade-offs?
5. Why metadata filters?
6. How do you measure RAG quality?
7. How do you reduce hallucinations?
8. How would you secure enterprise RAG?

## CV text — USE ONLY AFTER COMPLETION

- Built a Microsoft Foundry RAG application using Azure AI Search vector and hybrid retrieval over curated synthetic business content.
- Implemented chunking, metadata filtering, grounded prompting, citations and retrieval evaluation with failure-case testing.
- Added secure configuration and observability patterns using identity/Key Vault and Application Insights/Foundry tracing.
