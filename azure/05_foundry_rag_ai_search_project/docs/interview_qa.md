# Interview Questions and Easy Answers

## 1. Vector search vs keyword search?

Keyword search looks for lexical/text matches and is very strong for exact terms, IDs, names, and phrases. Vector search compares embeddings, so it can retrieve semantically similar text even when the wording is different.

## 2. Why hybrid retrieval?

Because keyword and vector search have complementary strengths. Hybrid search runs both and fuses the ranked results, so an exact identifier can benefit from keyword matching while natural-language intent can benefit from vectors.

## 3. What is RRF conceptually?

Reciprocal Rank Fusion combines multiple ranked result lists. Documents appearing high in one or more lists receive more weight. Azure AI Search uses RRF to merge full-text and vector results for hybrid queries.

## 4. Chunk-size trade-offs?

Small chunks are precise but can lose surrounding context and increase document/vector count. Large chunks preserve context but may contain unrelated material and waste tokens. Overlap helps prevent information loss at boundaries but costs extra storage/embedding work.

## 5. Why metadata filters?

Filters reduce the eligible search space using structured fields such as category, tenant, document type, region, or access label. They can improve relevance and are essential for authorization/security trimming in enterprise systems.

## 6. How do you measure RAG quality?

Separate retrieval and generation. Retrieval metrics include hit@k, recall@k, precision, MRR, and nDCG. Generation should check groundedness, answer correctness, citation correctness, unsupported-answer rate, latency, cost, and human task success.

## 7. How do you reduce hallucinations?

Use high-quality retrieval, explicit grounded prompting, fallback behavior for insufficient evidence, citations, smaller trusted context, confidence/evaluation gates, document version control, and continuous failure testing.

## 8. How would you secure enterprise RAG?

Use Microsoft Entra ID/managed identity, least-privilege RBAC, private endpoints where needed, Key Vault for remaining secrets, per-user authorization filters/security trimming, encryption, safe logging, data classification, prompt-injection defenses, monitoring, and audit controls.

## 9. Why does embedding dimension matter?

Every vector in one Azure AI Search vector field must match the dimensions defined by the index schema. Query vectors must also use the same embedding space/model configuration as indexed vectors.

## 10. What did this POC prove?

It proved end-to-end ingestion, vectorization, indexing, vector and hybrid retrieval, grounded response generation with source IDs, evaluation, failure testing, API serving, and optional observability/security patterns.
