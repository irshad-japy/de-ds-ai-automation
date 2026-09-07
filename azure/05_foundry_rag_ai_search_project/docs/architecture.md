# Architecture — POC-05

## Goal

Demonstrate retrieval quality and grounded generation rather than merely sending a prompt to an LLM.

## Data flow

```text
1. Markdown files
   -> 2. front-matter metadata parsing
   -> 3. token-aware chunking
   -> 4. Foundry embedding deployment
   -> 5. Azure AI Search index
   -> 6a. vector-only query
   -> 6b. hybrid query (keyword + vector)
   -> 7. top-k chunks
   -> 8. grounded prompt
   -> 9. Foundry chat deployment
   -> 10. answer + source identifiers
```

## Azure AI Search fields

Required by the original POC:

- `id`
- `title`
- `content`
- `source`
- `category`
- `chunk_id`
- `content_vector`

This implementation also adds `effective_date` to make the conflicting-policy test easier to reason about.

## Chunking strategy

Default:

- 300 tokens
- 50-token overlap

Why overlap exists: an answer-bearing sentence can cross an arbitrary chunk boundary. Overlap reduces the chance that important context is split apart.

Trade-off: more overlap improves continuity but increases index size, embedding cost, and duplicate retrieval.

## Vector vs keyword vs hybrid

- Keyword/full-text retrieval is strong when the query shares exact important words with the document.
- Vector retrieval is strong when wording differs but semantic meaning is similar.
- Hybrid retrieval submits both text and vector queries. Azure AI Search fuses the ranked result lists with RRF.

## Production extensions

- semantic reranking where tier/features support it;
- ACL/security trimming metadata;
- indexers and integrated vectorization for larger corpora;
- private endpoints;
- managed identity;
- Key Vault;
- model/search retries and circuit breaking;
- trace correlation;
- offline relevance judgments;
- automated prompt-injection evaluation;
- document versioning and stale-content removal.
