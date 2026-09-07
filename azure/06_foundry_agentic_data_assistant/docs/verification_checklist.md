# Final Verification Checklist

Mark every item only after you personally verify it.

- [ ] `python -m scripts.test_tools_local` passes.
- [ ] `pytest -q` passes.
- [ ] Azure SQL scripts 01, 02, and 04 execute successfully.
- [ ] Function App system-assigned managed identity is enabled.
- [ ] SQL identity has only EXECUTE on approved procedures for this POC.
- [ ] `GET /api/health` returns `status=ok`.
- [ ] `python -m scripts.verify_function_api` passes against Azure Function.
- [ ] `python -m search.verify_search` returns policy documents.
- [ ] Azure AI Search appears in Foundry Connected resources.
- [ ] `python -m agent.create_agent` creates an agent version.
- [ ] Revenue question selects `get_revenue_by_region`.
- [ ] Return-policy question uses Azure AI Search and includes a citation.
- [ ] Mixed order+policy question uses both structured data and search.
- [ ] Delete/write request is refused.
- [ ] Arbitrary SQL request is refused.
- [ ] Secret-exposure request is refused.
- [ ] `logs/agent_trace.jsonl` contains tool name, arguments, latency, failures, and final answer.
- [ ] Secrets are absent/redacted in trace logs.
- [ ] `python -m eval.run_evaluation` produces `eval/evaluation_results.json`.
- [ ] Security cases S01-S05 all pass safely.
