# POC-05 Evaluation Results

Date:

## Configuration

- Chat deployment:
- Embedding deployment:
- Embedding dimensions:
- Chunk size:
- Chunk overlap:
- Top-k:

## Aggregate metrics

| Metric | Result | Target/observation |
|---|---:|---|
| retrieval_hit@k | | Most expected sources should appear in top-k |
| citation_correct | | Supported answers should cite the right source |
| answer_grounded | | Should be high |
| unsupported_answer | | Should be 0 or very low |
| average latency | | Record only; POC baseline |

## Failure tests

| Test | Passed? | Notes |
|---|---|---|
| Not in corpus | | |
| Ambiguous question | | |
| Conflicting documents | | |
| Prompt injection in document | | |

## Vector vs hybrid comparison

Document at least 5 queries and note whether hybrid changed the top results.
