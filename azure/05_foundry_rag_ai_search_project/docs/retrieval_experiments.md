# Retrieval Experiments Log

Fill this in while running the POC.

## Configuration

- Date:
- Embedding deployment:
- Dimensions:
- Chunk size: 300
- Overlap: 50
- top-k: 5

## Experiment table

| Query | Vector top source | Hybrid top source | Expected source | Winner/notes |
|---|---|---|---|---|
| What is the return window for damaged items? | | | return_policy.md | |
| How quickly are standard domestic orders dispatched? | | | shipping_sla.md | |
| What is the first response target for P1? | | | support_policy.md | |
| Which field uniquely identifies an order? | | | data_dictionary_orders.md | |
| Which component stores vectors? | | | architecture_notes.md | |

## Chunk-size experiment

Try once with:

```dotenv
CHUNK_SIZE_TOKENS=150
CHUNK_OVERLAP_TOKENS=30
```

Delete/recreate the index and compare retrieval.

Then try:

```dotenv
CHUNK_SIZE_TOKENS=500
CHUNK_OVERLAP_TOKENS=75
```

Record whether larger chunks improve context or introduce noise.

## Failure-test notes

### Unsupported

Question:

Result:

Pass/fail:

### Ambiguous

Question:

Result:

Pass/fail:

### Conflicting sources

Question:

Result:

Pass/fail:

### Prompt injection in retrieved document

Question:

Result:

Pass/fail:
