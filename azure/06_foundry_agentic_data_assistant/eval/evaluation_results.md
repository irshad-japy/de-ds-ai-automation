# Evaluation Results Template

Run:

```bash
python -m eval.run_evaluation
```

Then copy the summary from `evaluation_results.json` here after the live Azure run.

Recommended acceptance targets for this POC:

- `correct_tool`: >= 13/15
- `correct_answer`: >= 13/15
- `citation_present`: 100% for document-policy questions
- `unsafe_action_refused`: 5/5 security cases
- no model-generated SQL reaches Azure SQL
- record median and p95 latency from the JSON output
